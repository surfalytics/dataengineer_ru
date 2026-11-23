#!/usr/bin/env python3
"""Update one book's row in scripts/book-tools/status.md.

Examples:
  # after a workflow run: read the stage markers and fill chapters, status, what is left
  status.py staff-engineer --group business --title "Staff Engineer" \
      --scratch /path/to/scratch --chapters 1,2,3,4,5,6,7,8

  # by hand: set the PR or a note
  status.py staff-engineer --pr "#107"
  status.py mom-test --status done --left "-"

  # lecture courses: their own status file, docs folder and lecNN markers
  status.py stanford-cs336 --kind lecture --group ai --title "Stanford CS336" \
      --scratch /path/to/scratch --chapters 1,2,3

Chapter status comes from the marker files in <scratch>/state/:
chNN.write.done, chNN.review.done, chNN.clarity.done. A chapter is done when it has
the clarity marker. The book is "done" when all chapters are done and index.md exists.
The date is today unless --date is given. A missing row is added at the end.
"""
import argparse
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
# unit: prefix of the stage markers (chNN.write.done, lecNN.write.done); final: the steps after all parts
KINDS = {
    "book": dict(file=ROOT / "scripts/book-tools/status.md", docs=ROOT / "src/content/docs/book-summaries",
                 unit="ch", final="overview, nav, cover, EPUB"),
    "lecture": dict(file=ROOT / "scripts/lecture-tools/status.md", docs=ROOT / "src/content/docs/lecture-summaries",
                    unit="lec", final="overview, nav, EPUB"),
}
# Column positions. The lecture file calls them Course and Lectures.
COLS = ["Book", "Folder", "Chapters", "Status", "Last revision", "PR", "What is left"]


def ranges(nums):
    """[1, 2, 3, 5] -> '1-3, 5'"""
    out, nums = [], sorted(nums)
    i = 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        out.append(str(nums[i]) if i == j else f"{nums[i]}-{nums[j]}")
        i = j + 1
    return ", ".join(out)


def from_markers(scratch, chapters, unit="ch"):
    state = pathlib.Path(scratch) / "state"
    has = lambda n, stage: (state / f"{unit}{n:02d}.{stage}.done").exists()
    done = [n for n in chapters if has(n, "clarity")]
    reviewed = [n for n in chapters if n not in done and has(n, "review")]
    written = [n for n in chapters if n not in done and n not in reviewed and has(n, "write")]
    missing = [n for n in chapters if n not in done + reviewed + written]
    left = []
    if reviewed:
        left.append(f"clarity: {unit} {ranges(reviewed)}")
    if written:
        left.append(f"review + clarity: {unit} {ranges(written)}")
    if missing:
        left.append(f"write: {unit} {ranges(missing)}")
    return done, left


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("slug")
    p.add_argument("--kind", choices=KINDS, default="book", help="book (default) or lecture")
    p.add_argument("--group", help="books: engineering, business, entrepreneurship, ai; lectures: ai, cs, data")
    p.add_argument("--title")
    p.add_argument("--scratch", help="workflow scratch dir with state/ markers")
    p.add_argument("--chapters", help="all chapter (or lecture) numbers, e.g. 0,1,2")
    p.add_argument("--status", help="override: done, needs review, in progress")
    p.add_argument("--pr")
    p.add_argument("--left", help="what is left; '-' for nothing")
    p.add_argument("--date", default=datetime.date.today().isoformat())
    a = p.parse_args()
    k = KINDS[a.kind]
    STATUS, DOCS = k["file"], k["docs"]

    lines = STATUS.read_text(encoding="utf-8").splitlines()
    idx = next((i for i, l in enumerate(lines) if f"/{a.slug}`" in l and l.startswith("|")), None)
    if idx is None:
        if not (a.group and a.title):
            sys.exit(f"no row for {a.slug}: pass --group and --title to add one")
        row = {c: "" for c in COLS}
        row.update({"Book": a.title, "Folder": f"`{a.group}/{a.slug}`", "PR": "—"})
    else:
        cells = [c.strip() for c in lines[idx].strip().strip("|").split("|")]
        row = dict(zip(COLS, cells))
    if a.title:
        row["Book"] = a.title
    if a.group:
        row["Folder"] = f"`{a.group}/{a.slug}`"

    if a.scratch and a.chapters:
        nums = [int(x) for x in a.chapters.split(",") if x.strip()]
        done, left = from_markers(a.scratch, nums, k["unit"])
        has_index = (DOCS / row["Folder"].strip("`") / "index.md").exists()
        if not has_index:
            left.append(k["final"])
        row["Chapters"] = f"{len(done)}/{len(nums)} done" if len(done) < len(nums) else str(len(nums))
        row["Status"] = "done" if not left else "in progress"
        row["What is left"] = "; ".join(left) or "—"

    if a.status:
        row["Status"] = a.status
    if a.pr:
        row["PR"] = a.pr
    if a.left:
        row["What is left"] = "—" if a.left == "-" else a.left
    row["Last revision"] = a.date

    new = "| " + " | ".join(row[c] or "—" for c in COLS) + " |"
    if idx is None:
        last = max(i for i, l in enumerate(lines) if l.startswith("|"))
        lines.insert(last + 1, new)
    else:
        lines[idx] = new
    STATUS.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(new)


if __name__ == "__main__":
    main()
