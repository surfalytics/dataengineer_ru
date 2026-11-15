#!/usr/bin/env python3
"""Turn a book (PDF or EPUB) into plain-text chapter files, so agents read text, not PDF pages.

Usage:
  # 1. Read the table of contents (PDF page numbers, not printed page numbers):
  pdftotext -f 1 -l 15 book.pdf - | less
  # 2. Split by PDF page ranges:
  python3 -I scripts/book-tools/split_source.py book.pdf OUT_DIR --chapters "1:15-40,2:41-70"
  # EPUB: one file per document in reading order (doc01.txt, doc02.txt, ...).
  # Code from <pre> blocks is kept between ``` fences.
  python3 -I scripts/book-tools/split_source.py book.epub OUT_DIR

Then count words: python3 -I scripts/book-tools/words.py OUT_DIR
Keep OUT_DIR in the scratchpad. Never commit book text.
"""
import argparse
import html.parser
import posixpath
import re
import subprocess
import sys
import zipfile
from pathlib import Path


def split_pdf(pdf, out, chapters):
    for part in chapters.split(","):
        num, rng = part.strip().split(":")
        first, last = rng.split("-")
        dst = out / f"ch{int(num):02d}.txt"
        r = subprocess.run(["pdftotext", "-f", first, "-l", last, str(pdf), str(dst)], capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"pdftotext failed for chapter {num} (pages {first}-{last}): {r.stderr.strip()}")
        print(f"{dst}  pages {first}-{last}")


class Text(html.parser.HTMLParser):
    BLOCK = {"p", "div", "li", "br", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "section", "figcaption"}

    def __init__(self):
        super().__init__()
        self.out, self.pre, self.skip = [], 0, 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        elif tag == "pre":
            self.pre += 1
            self.out.append("\n```\n")
        elif tag in ("h1", "h2", "h3", "h4"):
            self.out.append("\n" + "#" * int(tag[1]) + " ")
        elif tag in self.BLOCK:
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip -= 1
        elif tag == "pre":
            self.pre -= 1
            self.out.append("\n```\n")
        elif tag in self.BLOCK:
            self.out.append("\n")

    def handle_data(self, data):
        if self.skip:
            return
        self.out.append(data if self.pre else re.sub(r"\s+", " ", data))

    def text(self):
        return re.sub(r"\n\s*\n+", "\n\n", "".join(self.out)).strip() + "\n"


def split_epub(epub, out):
    z = zipfile.ZipFile(epub)
    opf_path = re.search(r'full-path="([^"]+)"', z.read("META-INF/container.xml").decode()).group(1)
    opf = z.read(opf_path).decode("utf-8", "replace")
    base = posixpath.dirname(opf_path)
    items = {}
    for m in re.finditer(r"<item\b[^>]*>", opf):
        tag = m.group(0)
        i, h = re.search(r'\bid="([^"]+)"', tag), re.search(r'\bhref="([^"]+)"', tag)
        if i and h:
            items[i.group(1)] = h.group(1)
    spine = re.findall(r'<itemref\b[^>]*\bidref="([^"]+)"', opf)
    n = 0
    for idref in spine:
        href = items.get(idref)
        if not href:
            continue
        p = Text()
        p.feed(z.read(posixpath.normpath(posixpath.join(base, href))).decode("utf-8", "replace"))
        txt = p.text()
        if len(txt.split()) < 50:  # cover, title page, empty
            continue
        n += 1
        dst = out / f"doc{n:02d}.txt"
        dst.write_text(txt, encoding="utf-8")
        first = next((l for l in txt.splitlines() if l.strip()), "")[:70]
        print(f"{dst}  {href}  | {first}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("book")
    ap.add_argument("out")
    ap.add_argument("--chapters", help='PDF only: "1:15-40,2:41-70" (chapter:first-last PDF page)')
    a = ap.parse_args()
    book, out = Path(a.book), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    if book.suffix.lower() == ".pdf":
        if not a.chapters:
            sys.exit("PDF needs --chapters. Read the table of contents first (see --help).")
        split_pdf(book, out, a.chapters)
    elif book.suffix.lower() == ".epub":
        split_epub(book, out)
    else:
        sys.exit("Only .pdf and .epub are supported.")


if __name__ == "__main__":
    main()
