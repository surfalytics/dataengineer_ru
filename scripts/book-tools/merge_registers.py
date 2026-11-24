#!/usr/bin/env python3
"""Merge the per-chapter registers of a book into the shared ones, then delete the parts.

  merge_registers.py <prefix>          # scripts/<prefix>-diagrams and scripts/<prefix>-code
  merge_registers.py <prefix> --dry    # print what would change, change nothing
  merge_registers.py <prefix> --unit lec   # lecture courses: glossary-lecNN.md, figures-lecNN.md, README-lecNN.md

- glossary-chNN.md -> glossary.md: table rows; a term already in glossary.md (first column, any case) is skipped.
- figures-chNN.md  -> figures.md: table rows; the header comes from the first part if figures.md is new.
- README-chNN.md   -> README.md (code folder): table rows go under "## Статус примеров" (added if missing);
  other text lines of a part go to "### Заметки по главам" as "Глава N: <line>".
Chapter order is kept. The workflow's Book step runs this instead of an agent merging by hand.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]


def is_row(l):
    return l.startswith("|") and not re.match(r"^\|[\s\-:|]+\|\s*$", l)


def table_parts(path):
    """header (title row + separator), data rows, other text lines"""
    lines = path.read_text(encoding="utf-8").splitlines()
    header, rows, other = [], [], []
    for i, l in enumerate(lines):
        if l.startswith("|"):
            if i + 1 < len(lines) and re.match(r"^\|[\s\-:|]+\|\s*$", lines[i + 1]) and not header:
                header = [l, lines[i + 1]]
            elif is_row(l) and l not in header:
                rows.append(l)
        elif l.strip() and not l.startswith("#"):
            other.append(l.strip())
    return header, rows, other


def chapter_of(row):
    m = re.match(r"^\|\s*(\d+)\s*\|", row)
    return int(m.group(1)) if m else None


def insert_rows(text, rows, after=""):
    """Put rows into the first table (after the line `after`, if given) in chapter order:
    before the first row of a later chapter, else at the end of the table. No table: return None."""
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if l.strip() == after), -1) if after else -1
    tbl = [i for i in range(start + 1, len(lines)) if lines[i].startswith("|")]
    if not tbl:
        return None
    first = tbl[0]
    end = first
    while end + 1 < len(lines) and lines[end + 1].startswith("|"):
        end += 1
    for r in rows:
        n = chapter_of(r)
        pos = end + 1  # default: end of the table
        if n is not None:
            for i in range(first + 2, end + 1):  # skip the header and separator lines
                c = chapter_of(lines[i])
                if c is not None and c > n:
                    pos = i
                    break
        lines.insert(pos, r)
        end += 1
    return "\n".join(lines) + "\n"


def key(row):
    return row.strip("|").split("|")[0].strip().strip("`").lower()


UNIT = "ch"  # set by --unit


def parts(folder, stem):
    return sorted(folder.glob(f"{stem}-{UNIT}[0-9][0-9].md"))


def merge_glossary(d, dry):
    target, ps = d / "glossary.md", parts(d, "glossary")
    if not ps:
        return "glossary: no parts"
    text = target.read_text(encoding="utf-8") if target.exists() else "| English | Как пишем | Не писать | Пояснение |\n|---|---|---|---|\n"
    have = {key(l) for l in text.splitlines() if is_row(l)}
    added, dup = [], 0
    for p in ps:
        for r in table_parts(p)[1]:
            if key(r) in have:
                dup += 1
                continue
            have.add(key(r))
            added.append(r)
    if not dry:
        target.write_text(text.rstrip("\n") + "\n" + "".join(r + "\n" for r in added), encoding="utf-8")
        for p in ps:
            p.unlink()
    return f"glossary: +{len(added)} rows, {dup} duplicates skipped, {len(ps)} parts"


def merge_figures(d, dry):
    target, ps = d / "figures.md", parts(d, "figures")
    if not ps:
        return "figures: no parts"
    rows, header = [], []
    for p in ps:
        h, r, _ = table_parts(p)
        header = header or h
        rows += r
    text = target.read_text(encoding="utf-8") if target.exists() else "# Figures\n\n" + "\n".join(header or ["| Глава | Figure | Идея | Наш файл | Статус |", "|---|---|---|---|---|"]) + "\n"
    merged = insert_rows(text, rows) or text.rstrip("\n") + "\n" + "".join(r + "\n" for r in rows)
    if not dry:
        target.write_text(merged, encoding="utf-8")
        for p in ps:
            p.unlink()
    return f"figures: +{len(rows)} rows, {len(ps)} parts"


def merge_readme(d, dry):
    target, ps = d / "README.md", parts(d, "README")
    if not ps:
        return "code README: no parts"
    rows, notes, header = [], [], []
    for p in ps:
        n = int(re.search(rf"{UNIT}(\d+)", p.name).group(1))
        h, r, o = table_parts(p)
        header = header or h
        rows += r
        notes += [f"- {'Лекция' if UNIT == 'lec' else 'Глава'} {n}: {l.lstrip('-* ')}" for l in o]
    text = target.read_text(encoding="utf-8") if target.exists() else "# Код конспекта\n"
    if "## Статус примеров" not in text:
        text = text.rstrip("\n") + "\n\n## Статус примеров\n"
    sec = text.split("## Статус примеров", 1)
    merged = insert_rows(text, rows, after="## Статус примеров")
    if merged is None:  # no table yet in the section
        merged = text.rstrip("\n") + "\n\n" + "\n".join(header or ["| Глава | Пример | Файл | Статус |", "|---|---|---|---|"]) + "\n" + "".join(r + "\n" for r in rows)
    if notes:
        merged = merged.rstrip("\n") + "\n\n### Заметки по " + ("лекциям" if UNIT == "lec" else "главам") + "\n\n" + "".join(l + "\n" for l in notes)
    if not dry:
        target.write_text(merged, encoding="utf-8")
        for p in ps:
            p.unlink()
    return f"code README: +{len(rows)} rows, {len(notes)} notes, {len(ps)} parts"


def main():
    global UNIT
    argv = sys.argv[1:]
    if "--unit" in argv:
        i = argv.index("--unit")
        UNIT = argv[i + 1]
        del argv[i:i + 2]
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1 or UNIT not in ("ch", "lec"):
        sys.exit(__doc__)
    dry = "--dry" in sys.argv
    prefix = args[0]
    diag, code = ROOT / f"scripts/{prefix}-diagrams", ROOT / f"scripts/{prefix}-code"
    print(merge_glossary(diag, dry))
    print(merge_figures(diag, dry))
    print(merge_readme(code, dry) if code.exists() else "code README: no code folder")


if __name__ == "__main__":
    main()
