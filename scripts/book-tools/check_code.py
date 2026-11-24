#!/usr/bin/env python3
"""Check the code blocks of a summary page without an LLM: run them and compare their output with the page.

  check_code.py <page.md> --code-dir scripts/<book>-code [--runner CMD] [--repeat 2] [--json]

What it does, block by block (in page order):
- ```python: finds the script in --code-dir that the block equals (exact) or is cut from (excerpt:
  every code line of the block is in the file). Runs that script with --runner (default: python3),
  --repeat times with different PYTHONHASHSEED values, and checks that the output is the same each time.
  The ```text block right under it must be part of the real output: each of its lines must be in
  the output ("..." lines are skipped, so a page may show a cut).
  A python block that matches no script is "unmatched": an agent has to check it.
- ```sql: all sql blocks run in order in one DuckDB session (duckdb CLI). The ```text block under
  a sql block must be part of that block's output.
- A python block with "# не запускается: <причина>" in its first 3 lines: "notrun", not a problem.
- Other languages (bash, yaml, scala...): counted as "other", not run.

A script can ask for its own environment with a header line, for example
  # runner-env: SPARK_IMAGE=learning-spark:4.2.0-delta
The runner gets "-I <script>" as arguments (it must accept python3 arguments).

Exit code 0 when no block is diff, error, unstable or unmatched.
"""
import argparse
import json
import os
import pathlib
import re
import shlex
import subprocess
import sys

FENCE = re.compile(r"^```(\w*)[^\n]*\n(.*?)^```", re.S | re.M)
SKIP = {"...", "…", "[...]"}
# a block that cannot run here says so in a comment in its first 3 lines
NOTRUN = re.compile(r"#.*(не запускается|не запускаем|not run)")


def blocks(text):
    out = []
    for m in FENCE.finditer(text):
        out.append({"lang": m.group(1).lower(), "body": m.group(2), "line": text.count("\n", 0, m.start()) + 1,
                    "start": m.start(), "end": m.end()})
    # the output block is the next block, if it is ```text and only prose (no other code) lies between
    for i, b in enumerate(out):
        b["out"] = None
        if b["lang"] in ("python", "py", "sql") and i + 1 < len(out) and out[i + 1]["lang"] in ("text", "txt", ""):
            b["out"] = out[i + 1]
    return out


def code_lines(s):
    """Code lines without comments and extra spaces, so a page excerpt matches its script."""
    out = []
    for l in s.splitlines():
        l = re.sub(r"\s+#\s.*$", "", l).strip()      # inline comment: code  # text
        if l and not l.startswith("#"):
            out.append(re.sub(r"\s+", " ", l))
    return out


def find_script(body, scripts, min_share=0.8):
    """exact: same text; excerpt: at least min_share of the block's code lines are in one script."""
    want = body.strip()
    for p, src in scripts.items():
        if src.strip() == want:
            return p, "exact"
    lines = code_lines(body)
    if not lines:
        return None, None
    best, share = None, 0.0
    for p, src in scripts.items():
        have = set(code_lines(src))
        s = sum(l in have for l in lines) / len(lines)
        if s > share:
            best, share = p, s
    return (best, "excerpt") if share >= min_share else (None, None)


BOX = re.compile(r"[│┃|┌┐└┘├┤┬┴┼─═╞╡╪+]")


def cells(line):
    """Table row as cells: the same row in box, column or '|' format gives the same cells."""
    return " ".join(BOX.sub(" ", line).split())


def missing_lines(expected, actual):
    have = {cells(l) for l in actual.splitlines()}
    miss = []
    for l in expected.splitlines():
        c = cells(l)
        if not c or l.strip() in SKIP:
            continue
        if c not in have:
            miss.append(l.rstrip())
    return miss


def run_script(path, runner, repeat, timeout):
    env_extra = {}
    for l in path.read_text(encoding="utf-8").splitlines()[:15]:
        m = re.match(r"#\s*runner-env:\s*(\w+)=(\S+)", l)
        if m:
            env_extra[m.group(1)] = m.group(2)
    outs = []
    for seed in range(1, repeat + 1):
        env = {**os.environ, **env_extra, "PYTHONHASHSEED": str(seed * 7919)}
        cmd = shlex.split(runner) + ["-I", str(path)]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=timeout)
        except subprocess.TimeoutExpired:
            return {"status": "error", "detail": f"timeout {timeout}s"}
        if r.returncode != 0:
            return {"status": "error", "detail": (r.stderr.strip().splitlines() or ["exit %d" % r.returncode])[-1][:300]}
        outs.append(r.stdout)
    if any(o != outs[0] for o in outs[1:]):
        return {"status": "unstable", "detail": "output differs between runs", "stdout": outs[0]}
    return {"status": "ok", "stdout": outs[0]}


def run_sql(sql_blocks):
    """Run sql blocks in one session; return the output of each block (or an error)."""
    script = ""
    for i, b in enumerate(sql_blocks):
        script += f"\n.print @@BLOCK {i}@@\n" + b["body"]
    script += "\n.print @@END@@\n"
    r = subprocess.run(["duckdb", "-bail", ":memory:"], input=script, text=True, capture_output=True)
    parts = re.split(r"^@@BLOCK (\d+)@@$", r.stdout, flags=re.M)
    res = {int(parts[k]): parts[k + 1].replace("@@END@@", "") for k in range(1, len(parts) - 1, 2)}
    err = r.stderr.strip() if r.returncode != 0 else ""
    return res, err


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page")
    ap.add_argument("--code-dir", required=True)
    ap.add_argument("--runner", default="python3")
    ap.add_argument("--repeat", type=int, default=2)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    page = pathlib.Path(a.page)
    text = page.read_text(encoding="utf-8")
    code_dir = pathlib.Path(a.code_dir)
    scripts = {p: p.read_text(encoding="utf-8") for p in sorted(code_dir.glob("*.py"))}
    bl = blocks(text)

    results, runs = [], {}
    sql_bl = [b for b in bl if b["lang"] == "sql"]
    sql_out, sql_err = run_sql(sql_bl) if sql_bl else ({}, "")
    for b in bl:
        if b["lang"] in ("text", "txt", "") or any(b is x["out"] for x in bl if x["out"]):
            continue
        r = {"line": b["line"], "lang": b["lang"] or "none"}
        if b["lang"] in ("python", "py"):
            path, how = find_script(b["body"], scripts)
            head = "\n".join(b["body"].splitlines()[:3]).lower()
            if NOTRUN.search(head):
                r.update(status="notrun", detail=head.splitlines()[0][:120])
            elif not path:
                r.update(status="unmatched", detail="no script in code dir has this code")
            else:
                r.update(script=str(path), match=how)
                if path not in runs:
                    runs[path] = run_script(path, a.runner, a.repeat, a.timeout)
                run = runs[path]
                r["status"] = run["status"]
                if run["status"] in ("error", "unstable"):
                    r["detail"] = run["detail"]
                elif b["out"]:
                    miss = missing_lines(b["out"]["body"], run["stdout"])
                    if miss:
                        r.update(status="diff", detail=f"{len(miss)} output lines not in real output, first: {miss[0][:120]}")
        elif b["lang"] == "sql":
            i = sql_bl.index(b)
            if i not in sql_out:
                r.update(status="error", detail=(sql_err.splitlines() or ["sql did not run"])[-1][:300])
            else:
                r["status"] = "ok"
                if b["out"]:
                    miss = missing_lines(b["out"]["body"], sql_out[i])
                    if miss:
                        r.update(status="diff", detail=f"{len(miss)} output lines not in real output, first: {miss[0][:120]}")
        else:
            r["status"] = "other"
        results.append(r)

    prefix = re.match(r"(\d+)-", page.name)
    unused = []
    if prefix:
        used = {pathlib.Path(r["script"]) for r in results if r.get("script")}
        unused = [str(p) for p in scripts if re.match(rf"(ch|lec){prefix.group(1)}_", p.name) and p not in used]
    count = {}
    for r in results:
        count[r["status"]] = count.get(r["status"], 0) + 1
    bad = [r for r in results if r["status"] in ("diff", "error", "unstable", "unmatched")]
    summary = {"page": str(page), "blocks": len(results), "count": count, "problems": bad, "unusedScripts": unused}
    if a.json:
        print(json.dumps(summary, ensure_ascii=False))
    else:
        for r in bad:
            print(f"{r['status'].upper():9} L{r['line']} {r['lang']} {r.get('script', '')} {r.get('detail', '')}")
        for u in unused:
            print(f"INFO      script not used on the page: {u}")
        print("-- " + ", ".join(f"{v} {k}" for k, v in sorted(count.items())))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
