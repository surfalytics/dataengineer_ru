#!/usr/bin/env python3
"""Check that the code on a lecture page is the code in the files, and its output is real.

  python3 -I scripts/lecture-tools/check_code.py <page.md> <code dir> --prefix lec01 [--python <venv>/bin/python]

For every <code dir>/<prefix>_*.py: the file's text must be a ```python block on the page, and the
script's output (run with --python, default: this python) must be a ```text block on the page.
Prints one line per file and exits 1 if any file differs. Run it after every edit of a page with code.
"""
import argparse
import pathlib
import re
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page")
    ap.add_argument("code_dir")
    ap.add_argument("--prefix", required=True, help="file prefix, e.g. lec01")
    ap.add_argument("--python", default=sys.executable, help="python of the venv with requirements.txt")
    a = ap.parse_args()

    text = pathlib.Path(a.page).read_text(encoding="utf-8")
    blocks = re.findall(r"^```(\w*)\n(.*?)^```", text, flags=re.S | re.M)
    py = [b for lang, b in blocks if lang == "python"]
    out = [b for lang, b in blocks if lang == "text"]
    files = sorted(pathlib.Path(a.code_dir).glob(f"{a.prefix}_*.py"))
    if not files:
        sys.exit(f"no {a.prefix}_*.py in {a.code_dir}")
    bad = 0
    for f in files:
        src = f.read_text(encoding="utf-8").rstrip("\n") + "\n"
        r = subprocess.run([a.python, "-I", str(f)], capture_output=True, text=True, timeout=600)
        if r.returncode:
            print(f"FAIL  {f.name}: exit {r.returncode}: {r.stderr.strip().splitlines()[-1:]}")
            bad += 1
            continue
        res = r.stdout.rstrip("\n") + "\n"
        code_ok, out_ok = src in py, (res == "\n" or res in out)
        bad += not (code_ok and out_ok)
        print(f"{'ok  ' if code_ok and out_ok else 'DIFF'}  {f.name}: code {'ok' if code_ok else 'not on page or changed'}, "
              f"output {'ok' if out_ok else 'not on page or changed'}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
