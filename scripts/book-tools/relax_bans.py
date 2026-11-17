#!/usr/bin/env python3
"""Drop glossary bans ("Не писать") that the existing pages already use.

Use it before a reviewOnly run of an older book. book-prep drafts a fresh glossary, and
its bans often hit normal Russian words the pages use on purpose (канал, ИИ, партиция).
A review agent would then replace hundreds of good words. This script keeps only the
bans that do not appear on the pages.

  relax_bans.py <glossary.md> <page.md> [<page.md> ...] [--dry-run]

Matching is the same as check.py: case-insensitive, Russian word endings allowed.
Prints each removed ban with its hit count.
"""
import re
import sys


def stem_pattern(word):
    """The same matcher as check.py uses for glossary bans, so both agree."""
    import importlib.util, pathlib
    path = pathlib.Path(__file__).resolve().parents[1] / "ru-proofread" / "check.py"
    spec = importlib.util.spec_from_file_location("ru_check", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.stem_regex(word.strip())


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    if len(args) < 2:
        sys.exit(__doc__)
    gpath, pages = args[0], args[1:]
    text = ""
    for p in pages:
        body = open(p, encoding="utf-8").read()
        text += re.sub(r"```.*?```", " ", body, flags=re.S) + "\n"
    out, removed = [], []
    for line in open(gpath, encoding="utf-8").read().splitlines():
        m = re.match(r"^(\| [^|]+? \| [^|]*? \| )([^|]*?)( \| .*)$", line)
        if not m or m.group(2).strip() in ("—", "-", "Не писать", "") or set(m.group(2).strip()) <= set("-: "):
            out.append(line)
            continue
        keep = []
        for ban in [b.strip(" `") for b in re.split(r"\s*[,;]\s*", m.group(2)) if b.strip(" `") and b.strip(" `") not in "—-"]:
            hits = len(stem_pattern(ban).findall(text))
            if hits:
                removed.append((ban, hits, line.split("|")[1].strip()))
            else:
                keep.append(ban)
        out.append(m.group(1) + (", ".join(keep) if keep else "—") + m.group(3))
    for ban, hits, term in sorted(removed, key=lambda x: -x[1]):
        print(f"{hits:>4}  {ban}  (term: {term})")
    print(f"removed {len(removed)} bans" + (" (dry run)" if dry else ""))
    if not dry:
        open(gpath, "w", encoding="utf-8").write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
