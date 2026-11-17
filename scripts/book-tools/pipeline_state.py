#!/usr/bin/env python3
"""Print the book-summary pipeline state of chapters as JSON, for the workflow's Status step.

  pipeline_state.py <scratch> "<n>|<src>|<page>" ["<n>|<src>|<page>" ...]

For each chapter: which stage markers exist in <scratch>/state/ (chNN.<stage>.done),
the page size in % of the source (words.py), and whether check.py --stats says LOW.
No page means pct 0. The output is the only source of truth: never guess these values.
"""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
STAGES = ["write", "review", "flow", "clarity", "code"]


def run(args):
    r = subprocess.run([sys.executable, "-I", *args], cwd=ROOT, capture_output=True, text=True)
    return r.stdout


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    state = pathlib.Path(sys.argv[1]) / "state"
    out = []
    for spec in sys.argv[2:]:
        n, src, page = spec.split("|")
        n = int(n)
        done = [s for s in STAGES if (state / f"ch{n:02d}.{s}.done").exists()]
        pct, low = 0.0, False
        if (ROOT / page).exists():
            m = re.search(r"([\d.]+)%", run(["scripts/book-tools/words.py", "--source", src, page]))
            pct = float(m.group(1)) if m else 0.0
            low = "LOW" in run(["scripts/ru-proofread/check.py", "--stats", page])
        out.append({"n": n, "done": done, "pct": pct, "statsLow": low})
    print(json.dumps({"chapters": out}))


if __name__ == "__main__":
    main()
