#!/usr/bin/env python3
"""Count prose words of a chapter page or a source chapter, and the size ratio.

Usage:
  python3 -I scripts/book-tools/words.py PAGE.md [PAGE2.md ...]      # prose words of pages
  python3 -I scripts/book-tools/words.py SOURCE_DIR                   # all .txt and .md files in a folder
  python3 -I scripts/book-tools/words.py --source ch03.txt PAGE.md    # page words as % of the source
  python3 -I scripts/book-tools/words.py --target 15-25 --source lec03.md PAGE.md   # lecture page

Prose means: no front matter, no ``` code blocks, no <details> blocks, no HTML tags, no URLs,
no video timestamps like [12:34] or [▶ 1:02:03].
For .txt from a PDF there are no code fences, so lines that look like code are dropped (an estimate).
Target (--target, default 20-40): book chapter page 20-40% of the source, aim for 30% (the middle).
Lecture page: 15-25% of the transcript, aim for 20% (see the lecture-summary skill).
"""
import argparse
import re
import sys
from pathlib import Path

WORD = re.compile(r"[^\W_]+(?:[-'’][^\W_]+)*")
CODE_LINE = re.compile(
    r"^\s*(\$ |>>> |\.\.\. |#!|def |class |import |from \S+ import |return\b|@\w)"
    r"|^\s*(SELECT|FROM|WHERE|GROUP BY|ORDER BY|JOIN|CREATE|INSERT|UPDATE|WITH)\b"
    r"|[;{}]\s*$|^\s*[\])}]+[,;]?\s*$|\w+\(.*\)\s*$|^\s*\w+\s*=\s*\S"
)
# Video timestamps in transcripts and lecture pages: [12:34], [1:02:03], [▶ 12:34], [12:34–15:00]
STAMP = re.compile(r"\[(?:▶\s*)?\d{1,2}(?::\d{2}){1,2}(?:\s*[–-]\s*\d{1,2}(?::\d{2}){1,2})?\]")


def prose(text, path):
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    text = re.sub(r"^```.*?^```[^\n]*$", "", text, flags=re.S | re.M)
    text = re.sub(r"<details>.*?</details>", "", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\]\([^)]*\)", "]", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = STAMP.sub(" ", text)
    if path.suffix == ".txt":
        text = "\n".join(l for l in text.splitlines() if not CODE_LINE.search(l))
    return text


def count(path):
    return len(WORD.findall(prose(path.read_text(encoding="utf-8"), path)))


def sections(path, share=0.30, hi=40):
    """Word budget per heading of a source chapter: plan the page before you write it."""
    text = path.read_text(encoding="utf-8")
    parts, title, buf, fence = [], "(start)", [], False
    for line in text.splitlines():
        if line.startswith("```"):
            fence = not fence
        m = None if fence else re.match(r"^(#{1,4})\s+(.*)", line)
        if m:
            parts.append((title, "\n".join(buf)))
            title, buf = m.group(1) + " " + m.group(2).strip(), []
        else:
            buf.append(line)
    parts.append((title, "\n".join(buf)))
    total = 0
    for t, body in parts:
        n = len(WORD.findall(prose(body, path)))
        if n == 0:
            continue
        total += n
        print(f"{n:6d}  budget {round(n * share):5d}  {t[:70]}")
    print(f"{total:6d}  budget {round(total * share):5d}  TOTAL (aim {round(share * 100)}%, max {hi}%)")
    if len(parts) < 3:
        print("No headings found (PDF text?). Split the budget by the chapter's own section list.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--source", help="source chapter (.txt or .md) to compare with")
    ap.add_argument("--sections", action="store_true", help="word budget per heading of a source (middle of --target)")
    ap.add_argument("--target", default="20-40", help="ok range in %% of the source, LO-HI (default 20-40)")
    a = ap.parse_args()
    lo, hi = (float(x) for x in a.target.split("-"))
    if a.sections:
        for p in a.paths:
            sections(Path(p), (lo + hi) / 200, round(hi))
        return
    files = []
    for p in map(Path, a.paths):
        files += sorted(f for f in p.iterdir() if f.suffix in (".txt", ".md")) if p.is_dir() else [p]
    src = count(Path(a.source)) if a.source else None
    if src is not None:
        print(f"{src:7d}  source  {a.source}")
    bad = False
    for f in files:
        n = count(f)
        if src:
            pct = n / src * 100
            mark = "ok" if lo <= pct <= hi else ("THIN" if pct < lo else "LONG")
            bad |= mark != "ok"
            print(f"{n:7d}  {pct:5.1f}%  {mark:4s}  {f}")
        else:
            print(f"{n:7d}  {f}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
