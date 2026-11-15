#!/usr/bin/env python3
"""Token use and estimated API cost of workflow runs, per agent and per phase.

Usage:
  python3 -I scripts/book-tools/token_usage.py <workflow transcript dir> [more dirs ...]
  python3 -I scripts/book-tools/token_usage.py --md <dir> ...      # Markdown tables

The transcript dir is printed when a workflow starts:
  ~/.claude/projects/<project>/<session>/subagents/workflows/wf_<id>/

Cost uses list API prices (USD per 1M tokens). On a subscription it shows the relative weight, not a bill.
Cache writes: 5-minute = 1.25x input, 1-hour = 2x input. Cache reads use the model's read price.
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

# model: (input, output, cache read)
PRICES = {
    "claude-opus-5-5": (4.0, 20.0, 0.20),
    "claude-sonnet-5-5": (2.0, 10.0, 0.10),
    "claude-haiku-5-5": (0.10, 0.50, 0.01),
    "claude-fable-5-2": (8.0, 40.0, 0.20),
}
FIELDS = ("in", "write", "read", "out")


def agent_usage(path):
    msgs = {}
    model = None
    for line in path.open(encoding="utf-8"):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        m = d.get("message") or {}
        if d.get("type") != "assistant" or not m.get("usage"):
            continue
        msgs[m.get("id") or len(msgs)] = (m.get("model"), m["usage"])  # last line per message wins
    tot = dict.fromkeys(FIELDS, 0)
    cost = 0.0
    for model, u in msgs.values():
        cc = u.get("cache_creation") or {}
        w5 = cc.get("ephemeral_5m_input_tokens", 0)
        w1 = cc.get("ephemeral_1h_input_tokens", 0)
        if not cc:
            w5 = u.get("cache_creation_input_tokens", 0)
        row = {"in": u.get("input_tokens", 0), "write": w5 + w1, "read": u.get("cache_read_input_tokens", 0), "out": u.get("output_tokens", 0)}
        for k in FIELDS:
            tot[k] += row[k]
        pi, po, pr = PRICES.get(model, PRICES["claude-opus-5-5"])
        cost += (row["in"] * pi + w5 * pi * 1.25 + w1 * pi * 2 + row["read"] * pr + row["out"] * po) / 1e6
    return model, len(msgs), tot, cost


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--md", action="store_true", help="print Markdown tables")
    a = ap.parse_args()
    rows = []
    for d in map(Path, a.dirs):
        for f in sorted(d.glob("agent-*.jsonl")):
            meta_p = f.with_suffix(".meta.json")
            meta = json.loads(meta_p.read_text()) if meta_p.exists() else {}
            model, turns, tot, cost = agent_usage(f)
            rows.append({"run": d.name, "label": meta.get("description", f.stem), "phase": meta.get("workflowPhase", ""),
                         "model": (model or "?").replace("claude-", ""), "turns": turns, **tot, "cost": cost})
    if not rows:
        raise SystemExit("no agent transcripts found")

    def k(n):
        return f"{n / 1000:.0f}K" if n >= 1000 else str(n)

    head = ["agent", "phase", "model", "turns", "input", "cache write", "cache read", "output", "est. $"]
    sep = " | " if a.md else "  "

    def line(cells):
        return ("| " + " | ".join(cells) + " |") if a.md else sep.join(f"{c:>12}" if i > 2 else f"{c:<14}" for i, c in enumerate(cells))

    print(line(head))
    if a.md:
        print("|" + "---|" * len(head))
    for r in rows:
        print(line([r["label"], r["phase"], r["model"], str(r["turns"]), k(r["in"]), k(r["write"]), k(r["read"]), k(r["out"]), f"{r['cost']:.2f}"]))
    ph = defaultdict(lambda: dict.fromkeys(FIELDS + ("cost", "agents"), 0))
    for r in rows:
        for f in FIELDS + ("cost",):
            ph[r["phase"]][f] += r[f]
        ph[r["phase"]]["agents"] += 1
    print()
    print(line(["phase", "agents", "", "", "input", "cache write", "cache read", "output", "est. $"]))
    if a.md:
        print("|" + "---|" * len(head))
    for p, t in ph.items():
        print(line([p, str(t["agents"]), "", "", k(t["in"]), k(t["write"]), k(t["read"]), k(t["out"]), f"{t['cost']:.2f}"]))
    T = {f: sum(r[f] for r in rows) for f in FIELDS + ("cost",)}
    print(line(["TOTAL", str(len(rows)), "", "", k(T["in"]), k(T["write"]), k(T["read"]), k(T["out"]), f"{T['cost']:.2f}"]))


if __name__ == "__main__":
    main()
