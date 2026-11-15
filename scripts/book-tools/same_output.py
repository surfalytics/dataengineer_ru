#!/usr/bin/env python3
"""Run a script several times and check that the output is the same every time.

Prints one short line instead of all the output. Use it for the "deterministic code" rule.

Usage:
  python3 -I scripts/book-tools/same_output.py scripts/<book>-code/ch03_x.py
  python3 -I scripts/book-tools/same_output.py -n 6 --python scripts/<book>-code/.venv/bin/python script.py

Each run uses `python -I`, so hash randomization stays on.
Exit code: 0 if all runs match, 1 if they differ or a run fails.
"""
import argparse
import difflib
import hashlib
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script")
    ap.add_argument("args", nargs="*")
    ap.add_argument("-n", type=int, default=6, help="number of runs (default 6)")
    ap.add_argument("--python", default=sys.executable)
    a = ap.parse_args()
    runs = []
    for _ in range(a.n):
        r = subprocess.run([a.python, "-I", a.script, *a.args], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"FAIL exit {r.returncode}: {a.script}")
            print("\n".join(r.stderr.strip().splitlines()[-15:]))
            sys.exit(1)
        runs.append(r.stdout)
    hashes = {hashlib.sha256(o.encode()).hexdigest()[:12] for o in runs}
    if len(hashes) == 1:
        print(f"same x{a.n}  {len(runs[0].splitlines())} lines  {a.script}")
        return
    other = next(o for o in runs if o != runs[0])
    print(f"DIFF: {len(hashes)} different outputs in {a.n} runs  {a.script}")
    diff = difflib.unified_diff(runs[0].splitlines(), other.splitlines(), "run 1", "other run", lineterm="", n=1)
    print("\n".join(list(diff)[:30]))
    sys.exit(1)


if __name__ == "__main__":
    main()
