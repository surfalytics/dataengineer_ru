#!/usr/bin/env python3
"""Count prose words of a chapter page or a source chapter, and the size ratio.

Usage:
  python3 -I scripts/book-tools/words.py PAGE.md [PAGE2.md ...]      # prose words of pages
  python3 -I scripts/book-tools/words.py SOURCE_DIR                   # all .txt and .md files in a folder
  python3 -I scripts/book-tools/words.py --source ch03.txt PAGE.md    # page words as % of the source

Prose means: no front matter, no ``` code blocks, no <details> blocks, no HTML tags, no URLs.
For .txt from a PDF there are no code fences, so lines that look like code are dropped (an estimate).
Target for a chapter page: 20-40% of the source, aim for 30%.
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


def prose(text, path):
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    text = re.sub(r"^```.*?^```[^\n]*$", "", text, flags=re.S | re.M)
    text = re.sub(r"<details>.*?</details>", "", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\]\([^)]*\)", "]", text)
    text = re.sub(r"https?://\S+", " ", text)
    if path.suffix == ".txt":
        text = "\n".join(l for l in text.splitlines() if not CODE_LINE.search(l))
    return text


def count(path):
    return len(WORD.findall(prose(path.read_text(encoding="utf-8"), path)))


def sections(path, share=0.30):
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
    print(f"{total:6d}  budget {round(total * share):5d}  TOTAL (aim {int(share * 100)}%, max 40%)")
    if len(parts) < 3:
        print("No headings found (PDF text?). Split the budget by the chapter's own section list.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--source", help="source chapter (.txt or .md) to compare with")
    ap.add_argument("--sections", action="store_true", help="word budget per heading of a source chapter (30%%)")
    a = ap.parse_args()
    if a.sections:
        for p in a.paths:
            sections(Path(p))
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
            mark = "ok" if 20 <= pct <= 40 else ("THIN" if pct < 20 else "LONG")
            bad |= mark != "ok"
            print(f"{n:7d}  {pct:5.1f}%  {mark:4s}  {f}")
        else:
            print(f"{n:7d}  {f}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
