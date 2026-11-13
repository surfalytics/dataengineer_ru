#!/usr/bin/env python3
"""Deterministic Russian checks for Markdown pages of dataengineer.ru.

Run:  python3 -I scripts/ru-proofread/check.py [--strict] [--glossary FILE] FILE_OR_DIR ...

What it checks (prose only; front matter, code blocks, inline code, URLs are skipped):
  ERROR  straight quotes, "--", banned calques marked "error" in calques.tsv
  WARN   missing dash before "это", calques/stop words from calques.tsv,
         hyphen instead of dash, hyphen in number range, long sentences,
         three sentences in a row with the same first word,
         wrong spelling of a term (glossary column "Не писать")

Exit code: 1 if there is any ERROR (or any WARN with --strict), else 0.
Silence a line:   <!-- ru-proofread:ignore-line -->   (put it on the line before)
Silence a block:  <!-- ru-proofread:ignore-start --> ... <!-- ru-proofread:ignore-end -->
"""
import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CODE = "⟦код⟧"
MAX_WORDS = 30

# Words after which "это" is normal (no dash needed).
NO_DASH_BEFORE_ETO = set(
    """
    что как и а но или если то когда почему зачем где куда откуда ведь тогда поэтому значит
    всё все это там тут тоже также ещё еще уже именно только даже же ли не ни да нет
    потому чтобы хоть хотя будто словно кстати например итак вот ибо тем чем лишь
    из от для при о об про на в во с со к ко по за над под без до через между
    пока пусть пускай либо ни бы всегда иногда обычно часто редко сразу тоже почти
    сейчас теперь затем потом дальше снова опять лучше хуже можно нужно надо нельзя
    очень совсем вовсе просто сам сама само сами каждый каждая каждое
    я ты он она мы вы они мне тебе ему ей нам вам им меня тебя его её их
    делает делают сделать делать значит означает означают
    """.split()
)

# Sentences that start with these words are not definitions ("Как это работает", "На практике это ...").
ETO_SKIP_FIRST = set(
    """
    сколько как почему зачем что чем где когда куда откуда чему кто какой какая какое какие чей
    если пока раз чтобы хотя потому поскольку так тогда там тут здесь сначала затем потом
    в во на при для из по с со к ко о об от до за над под без через между про у
    да нет но а и или либо однако зато
    """.split()
)
# After "это" these words mean "это" is an object or a pronoun, not a copula.
ETO_SKIP_NEXT = set(
    """
    на в во с со к ко по за из для при около через до от у о об про над под без между
    как так что чтобы потому поэтому тоже также уже ещё еще можно нужно надо нельзя
    значит означает
    """.split()
)
# Endings of verbs (and some adverbs): the word before/after "это" is not a noun.
VERB_END = re.compile(
    r"(ет|ит|ют|ут|ат|ят|ёт|ешь|ишь|ем|ете|ите|ать|ять|ить|еть|уть|ыть|оть|ти|чь|ал|ил|ел|ол|ул|ыл|ли|ла|ло|ся|сь|ается|ется|ются|ски)$"
)

SENT_SPLIT = re.compile(r"(?<=[.!?…])\s+(?=[«\"A-ZА-ЯЁ⟦0-9(])")
WORD = re.compile(r"[A-Za-zА-Яа-яЁё][A-Za-zА-Яа-яЁё\-’']*")


class Finding:
    def __init__(self, path, line, level, rule, msg, ctx):
        self.path, self.line, self.level, self.rule, self.msg, self.ctx = path, line, level, rule, msg, ctx

    def __str__(self):
        ctx = self.ctx.strip()
        if len(ctx) > 110:
            ctx = ctx[:110] + "…"
        return f"{self.path}:L{self.line} [{self.level}] {self.rule}: {self.msg}\n    {ctx}"


def load_calques():
    rules = []
    p = HERE / "calques.tsv"
    for raw in p.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.startswith("#"):
            continue
        cols = raw.split("\t")
        if len(cols) < 3:
            continue
        pat, fix, sev = cols[0], cols[1], cols[2].strip().lower()
        why = cols[3] if len(cols) > 3 else ""
        rules.append((re.compile(pat, re.IGNORECASE), fix, "ERROR" if sev == "error" else "WARN", why))
    return rules


def load_glossary_bans(path):
    """Read a glossary table. If a column is named 'Не писать', ban those spellings."""
    bans = []
    if not path:
        return bans
    header = None
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        if not raw.strip().startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in raw.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", c) for c in cells):
            continue
        if header is None:
            header = cells
            continue
        if "Не писать" in header and len(cells) == len(header):
            bad = cells[header.index("Не писать")]
            good = cells[header.index("Как пишем")] if "Как пишем" in header else ""
            for b in re.split(r"\s*[,;/]\s*", bad):
                b = b.strip(" `")
                if b and b != "—":
                    bans.append((re.compile(re.escape(b), re.IGNORECASE), good))
    return bans


def prose_units(text):
    """Yield (line_no, unit_text). Table rows are split into cells."""
    lines = text.split("\n")
    i, n = 0, len(lines)
    in_front = in_code = in_ignore = False
    ignore_next = False
    if lines and lines[0].strip() == "---":
        in_front = True
        i = 1
    while i < n:
        raw = lines[i]
        no = i + 1
        i += 1
        if in_front:
            if raw.strip() == "---":
                in_front = False
            continue
        s = raw.strip()
        if s.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if "ru-proofread:ignore-start" in s:
            in_ignore = True
            continue
        if "ru-proofread:ignore-end" in s:
            in_ignore = False
            continue
        if "ru-proofread:ignore-line" in s:
            ignore_next = True
            continue
        if in_ignore or not s:
            ignore_next = False if not s else ignore_next
            continue
        if ignore_next:
            ignore_next = False
            continue
        if s.startswith("<") or s.startswith("![") or s.startswith("import "):
            continue
        if re.fullmatch(r"\|?[\s:|-]+\|[\s:|-]*", s):
            continue
        # clean markup
        c = re.sub(r"`[^`]*`", CODE, raw)
        c = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", c)
        c = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", c)
        c = re.sub(r"https?://\S+", CODE, c)
        c = re.sub(r"<[^>]+>", "", c)
        c = c.replace("**", "").replace("__", "")
        c = re.sub(r"^\s*(?:[-*+]|\d+\.)\s+", "", c)
        c = re.sub(r"^\s*#+\s+", "", c)
        c = re.sub(r"^\s*>\s?", "", c)
        c = re.sub(r"^\s*\*\*?Пояснение:?\*?\*?", "", c)
        if s.startswith("|"):
            for cell in c.strip().strip("|").split("|"):
                if cell.strip():
                    yield no, cell.strip()
        else:
            yield no, c.strip()


def split_sentences(unit):
    return [x for x in SENT_SPLIT.split(unit) if x.strip()]


def check_text(path, text, calques, bans):
    out = []

    def add(line, level, rule, msg, ctx):
        out.append(Finding(path, line, level, rule, msg, ctx))

    for no, unit in prose_units(text):
        # --- typography
        if '"' in unit:
            add(no, "ERROR", "quotes", 'Прямые кавычки в тексте. Используйте «ёлочки».', unit)
        if re.search(r"(?<!-)--(?!-)", unit):
            add(no, "ERROR", "double-hyphen", 'Два дефиса "--". Используйте тире «—» или перестройте фразу.', unit)
        if re.search(r"\s-\s", unit):
            add(no, "WARN", "hyphen-as-dash", "Дефис с пробелами вместо тире «—».", unit)
        for m in re.finditer(r"(?<![\w.-])(\d{1,4})-(\d{1,4})(?![\w-])", unit):
            if m.group(1) != m.group(2):
                add(no, "WARN", "range-hyphen", f"Диапазон «{m.group(0)}»: нужно короткое тире «{m.group(1)}–{m.group(2)}».", unit)
        if re.search(r"(->|=>|→|⇒)", unit):
            add(no, "WARN", "arrow", "Стрелка в тексте. Напишите словами.", unit)
        if re.search(r"[А-Яа-яЁё] {2,}[А-Яа-яЁё]", unit):
            add(no, "WARN", "double-space", "Двойной пробел.", unit)

        # --- missing dash before «это» (high precision: definition "X это Y" near the sentence start)
        for sent in split_sentences(unit):
            ws = re.findall(r"\S+", sent)
            low = [w.strip(".,:;!?()«»\"—–-").lower() for w in ws]
            if not low or low[0] in ETO_SKIP_FIRST:
                continue
            for k in range(1, min(len(ws) - 1, 6)):
                if low[k] != "это":
                    continue
                prev, nxt = ws[k - 1], low[k + 1]
                if prev[-1] in ",:;—–-(«\"" or low[k - 1] in NO_DASH_BEFORE_ETO or not low[k - 1]:
                    break
                if VERB_END.search(low[k - 1]) or VERB_END.search(nxt) or nxt in ETO_SKIP_NEXT:
                    break
                add(no, "WARN", "dash-before-eto", f"Возможно, нужно тире: «{prev} — это {ws[k + 1]}».", sent)
                break

        # --- calques, stop words
        for rx, fix, level, why in calques:
            m = rx.search(unit)
            if m:
                add(no, level, "calque", f"«{m.group(0)}» → {fix}" + (f" ({why})" if why else ""), unit)

        # --- glossary: wrong spelling of a term
        for rx, good in bans:
            m = rx.search(unit)
            if m:
                add(no, "ERROR", "glossary", f"«{m.group(0)}» нельзя. В глоссарии: {good}.", unit)

        # --- flow
        sents = split_sentences(unit)
        for s in sents:
            words = [w for w in WORD.findall(s)]
            if len(words) > MAX_WORDS:
                add(no, "WARN", "long-sentence", f"Предложение из {len(words)} слов. Разбейте на 2–3.", s)
        firsts = []
        for s in sents:
            ws = WORD.findall(s)
            firsts.append(ws[0].lower() if ws else "")
        for k in range(len(firsts) - 2):
            if firsts[k] and firsts[k] == firsts[k + 1] == firsts[k + 2] and len(firsts[k]) > 2:
                add(no, "WARN", "same-opener", f"Три предложения подряд начинаются с «{firsts[k]}». Измените ритм.", unit)
                break
    return out


def iter_files(paths):
    for p in paths:
        p = Path(p)
        if p.is_dir():
            yield from sorted(p.rglob("*.md"))
            yield from sorted(p.rglob("*.mdx"))
        else:
            yield p


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--strict", action="store_true", help="exit 1 on WARN too")
    ap.add_argument("--glossary", help="glossary.md with an optional «Не писать» column")
    ap.add_argument("--summary", action="store_true", help="print only counts per rule")
    ap.add_argument("--only", help="comma-separated rule names to show")
    a = ap.parse_args()

    calques = load_calques()
    bans = load_glossary_bans(a.glossary)
    only = set(a.only.split(",")) if a.only else None
    findings = []
    for f in iter_files(a.paths):
        findings += check_text(str(f), f.read_text(encoding="utf-8"), calques, bans)
    if only:
        findings = [x for x in findings if x.rule in only]

    if a.summary:
        from collections import Counter

        c = Counter((x.level, x.rule) for x in findings)
        for (lvl, rule), n in sorted(c.items(), key=lambda kv: -kv[1]):
            print(f"{n:5d}  {lvl:5s}  {rule}")
    else:
        for x in findings:
            print(x)
    errs = sum(1 for x in findings if x.level == "ERROR")
    warns = len(findings) - errs
    print(f"-- {errs} error, {warns} warn", file=sys.stderr)
    sys.exit(1 if errs or (a.strict and warns) else 0)


if __name__ == "__main__":
    main()
