#!/usr/bin/env python3
"""Deterministic Russian checks for Markdown pages of dataengineer.ru.

Check:   python3 -I scripts/ru-proofread/check.py [--glossary FILE] FILE_OR_DIR ...
Stats:   python3 -I scripts/ru-proofread/check.py --stats FILE_OR_DIR ...
Guard:   python3 -I scripts/ru-proofread/check.py --before OLD.md [--max-change 5] NEW.md
Fix:     python3 -I scripts/ru-proofread/check.py --fix FILE ...

Only prose is checked. Front matter, code blocks, inline code, URLs and HTML tags are skipped.

  ERROR  quotes, double-hyphen, calque (marked "error" in calques.tsv), glossary
  WARN   dash-before-eto, calque, term-drift, yo, decimal-point, doubled-word,
         hyphen-as-dash, range-hyphen, arrow, double-space,
         long-sentence, same-opener, choppy

--stats    rhythm numbers per page (sentence length, short sentences, link words).
--before   compares NEW with OLD: code, inline code, links, numbers, headings and
           front matter must be the same. Use it after every proofreading pass.
--fix      rewrites the file: "quotes" to «quotes», 00-99 to 00–99. Nothing else.

Exit code: 1 if there is any ERROR (or any WARN with --strict), else 0.
Silence a line:   <!-- ru-proofread:ignore-line -->   (put it on the line before)
Silence a block:  <!-- ru-proofread:ignore-start --> ... <!-- ru-proofread:ignore-end -->
"""
import argparse
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CODE = "⟦код⟧"

# --- limits. Change them here.
MAX_WORDS = 30  # long-sentence
SHORT_WORDS = 5  # a "short" sentence in --stats
CHOPPY_WORDS = 6  # choppy: sentences of this many words or fewer ...
CHOPPY_RUN = 4  # ... this many in a row, in one paragraph
# Flow targets for --stats. Taken from our best-reading summary (Data Warehouse Toolkit).
TARGET_MEDIAN = 8  # median words per sentence, at least
TARGET_SHORT = 30  # % of sentences with <= SHORT_WORDS words, at most
TARGET_LINKS = 10  # link words per 100 sentences, at least

LINK_WORDS = re.compile(
    r"\b(поэтому|потому что|так как|но|однако|зато|из-за этого|иначе говоря|то есть|например|значит|"
    r"при этом|в итоге|так что|кроме того|тогда|иначе|а значит|в результате|для этого|из-за)\b",
    re.IGNORECASE,
)

# Function words: "это" after them is not a copula.
NO_DASH_BEFORE_ETO = set(
    """
    что как и а но или если то когда почему зачем где куда откуда ведь тогда поэтому значит
    всё все это там тут тоже также ещё еще уже именно только даже же ли не ни да нет
    потому чтобы хоть хотя будто словно кстати например итак вот ибо тем чем лишь
    из от для при о об про на в во с со к ко по за над под без до через между
    пока пусть пускай либо бы всегда иногда обычно часто редко сразу почти
    сейчас теперь затем потом дальше снова опять лучше хуже чаще реже можно нужно надо нельзя
    очень совсем вовсе просто сам сама само сами каждый каждая каждое
    я ты он она мы вы они мне тебе ему ей нам вам им меня тебя его её их
    делает делают сделать делать означает означают
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
# Verb endings (and "-ски" adverbs). A word with such an ending next to "это" is not a noun.
VERB_END = re.compile(
    r"(ет|ит|ют|ут|ат|ят|ёт|ешь|ишь|ем|ете|ите|ать|ять|ить|еть|уть|ыть|оть|(?<!с)ти|чь"
    r"|ал|ил|ел|ол|ул|ыл|ли|ла|ло|ся|сь|ски)$"
)
# Nouns and numerals that end like verbs. Add more when the check misses a definition.
NOUNS_LIKE_VERBS = set(
    """
    результат формат агрегат автомат стандарт аппарат
    лимит кредит аудит коммит транзит бит
    пакет бюджет приоритет интернет ответ совет секрет
    маршрут атрибут институт
    интервал сигнал канал материал портал журнал терминал оригинал
    раздел предел отдел
    протокол символ
    число числа правило правила начало тело
    модели цели роли детали таблицы
    память сеть запись подпись смесь часть нить
    пять шесть семь восемь девять десять
    """.split()
)

YO_WORDS = [
    (re.compile(r"\bеще\b", re.I), "ещё"),
    (re.compile(r"\bн?ее\b", re.I), "её / неё"),
    (re.compile(r"\b(идет|дает|берет|ведет|придет|найдет)\b", re.I), "идёт, даёт, берёт…"),
    (re.compile(r"\b(под|рас|у)?счет\b|\b(рас|у)чет", re.I), "счёт, расчёт, учёт"),
    (re.compile(r"\bобъем", re.I), "объём"),
    (re.compile(r"\bнадежн", re.I), "надёжн…"),
    (re.compile(r"\bпричем\b|\bвсе-таки\b", re.I), "причём, всё-таки"),
]
# A number with a dot is fine after these words: "версия 1.2", "глава 5.1", "Airflow 3.4".
DOT_OK_BEFORE = re.compile(r"(верси\w*|v|глав\w*|раздел\w*|част\w*|рис|рисун\w*|figure|шаг\w*|табл\w*|листинг\w*|п|гл|[A-Za-z][\w.+-]*)\.?$", re.I)
ABBR = re.compile(r"(?:^|\s)(гл|см|рис|табл|стр|т|д|е|п|пр|напр|англ|ок|г|млн|млрд|тыс|vs|etc|e\.g|i\.e)\.$", re.I)
SENT_SPLIT = re.compile(r"(?<=[.!?…])\s+(?=[«\"A-ZА-ЯЁ⟦0-9(])")
WORD = re.compile(r"[A-Za-zА-Яа-яЁё][A-Za-zА-Яа-яЁё\-’']*")
RANGE = re.compile(r"(?<![\w.-])(\d{1,4})-(\d{1,4})(?![\w-])")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
NAV = re.compile(r"^(Предыдущая|Следующая|Назад|Далее)\b")  # page navigation line, not prose
PROTECTED = re.compile(r"`[^`]*`|\]\([^)]*\)|https?://\S+|<[^>]+>|\{[^}]*\}")


class Finding:
    def __init__(self, path, line, level, rule, msg, ctx=""):
        self.path, self.line, self.level, self.rule, self.msg, self.ctx = path, line, level, rule, msg, ctx

    def __str__(self):
        ctx = self.ctx.strip()
        if len(ctx) > 110:
            ctx = ctx[:110] + "…"
        head = f"{self.path}:L{self.line} [{self.level}] {self.rule}: {self.msg}"
        return head + (f"\n    {ctx}" if ctx else "")


# ---------------------------------------------------------------- data files


def read_tsv(name, min_cols):
    rows = []
    for raw in (HERE / name).read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.startswith("#"):
            continue
        cols = [c.strip() for c in raw.split("\t")]
        if len(cols) >= min_cols:
            rows.append(cols)
    return rows


def load_calques():
    rules = []
    for cols in read_tsv("calques.tsv", 3):
        why = cols[3] if len(cols) > 3 else ""
        level = "ERROR" if cols[2].lower() == "error" else "WARN"
        rules.append((re.compile(cols[0], re.IGNORECASE), cols[1], level, why))
    return rules


def load_term_pairs():
    """Russian stem + English term that mean the same thing. Both on one page = term drift."""
    return [(c[0].lower(), c[1].lower()) for c in read_tsv("term-pairs.tsv", 2)]


def stem_regex(phrase):
    """Regex for a phrase that also matches its inflected forms: потребитель -> потребителей."""
    parts = []
    for w in phrase.split():
        if re.fullmatch(r"[А-Яа-яЁё-]+", w):
            if len(w) >= 6:
                parts.append(re.escape(w[:-2]) + r"[а-яё]{0,4}")
            elif len(w) == 5 and w[-1] in "аеёиоуыэюяьй":
                parts.append(re.escape(w[:-1]) + r"[а-яё]{0,3}")
            else:
                parts.append(re.escape(w) + r"[а-яё]{0,3}")
        else:
            parts.append(re.escape(w))
    return re.compile(r"(?<![\w-])" + r"\s+".join(parts) + r"(?![\w-])", re.IGNORECASE)


def load_glossary_bans(path):
    """Read a glossary table. Spellings in the column «Не писать» are banned (with inflected forms)."""
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
            for b in re.split(r"\s*[,;]\s*", bad):
                b = b.strip(" `")
                if b and b not in "—-":
                    bans.append((stem_regex(b), good))
    return bans


# ---------------------------------------------------------------- markdown


def classify(text):
    """Yield (index, raw_line, kind). kind: front, code, skip, table, heading, prose."""
    lines = text.split("\n")
    in_front = bool(lines) and lines[0].strip() == "---"
    fence = None
    in_ignore = ignore_next = False
    for i, raw in enumerate(lines):
        s = raw.strip()
        if in_front:
            yield i, raw, "front"
            if i > 0 and s == "---":
                in_front = False
            continue
        m = FENCE.match(raw)
        if fence:
            yield i, raw, "code"
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) and s == m.group(1):
                fence = None
            continue
        if m:
            fence = m.group(1)
            yield i, raw, "code"
            continue
        if "ru-proofread:ignore-start" in s:
            in_ignore = True
        elif "ru-proofread:ignore-end" in s:
            in_ignore = False
        elif "ru-proofread:ignore-line" in s:
            ignore_next = True
            yield i, raw, "skip"
            continue
        elif not s:
            pass
        elif in_ignore or ignore_next:
            ignore_next = False
        elif s.startswith("<") or s.startswith("![") or s.startswith("import ") or s.startswith("export "):
            pass
        elif re.fullmatch(r"\|?[\s:|-]+\|[\s:|-]*", s):
            pass
        elif s.startswith("|"):
            yield i, raw, "table"
            continue
        elif re.match(r"#+\s", s):
            yield i, raw, "heading"
            continue
        else:
            yield i, raw, "prose"
            continue
        yield i, raw, "skip"


def clean(raw, keep_code=False):
    c = re.sub(r"`([^`]*)`", r"\1" if keep_code else CODE, raw)
    c = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", c)
    c = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", c)
    c = re.sub(r"https?://\S+", CODE, c)
    c = re.sub(r"<[^>]+>", "", c)
    c = c.replace("**", "").replace("__", "")
    c = re.sub(r"^\s*(?:[-*+]|\d+\.)\s+", "", c)
    c = re.sub(r"^\s*#+\s+", "", c)
    c = re.sub(r"^\s*>\s?", "", c)
    return c.strip()


def prose_units(text, keep_code=False):
    """Yield (line_no, unit_text, kind). kind: p (paragraph, list item), cell, h."""
    for i, raw, kind in classify(text):
        if kind == "prose":
            c = clean(raw, keep_code)
            if c:
                yield i + 1, c, "p"
        elif kind == "heading":
            yield i + 1, clean(raw, keep_code), "h"
        elif kind == "table":
            for cell in clean(raw, keep_code).strip("|").split("|"):
                if cell.strip():
                    yield i + 1, cell.strip(), "cell"


def split_sentences(unit):
    out = []
    for piece in SENT_SPLIT.split(unit):
        if not piece.strip():
            continue
        if out and ABBR.search(out[-1]):
            out[-1] += " " + piece
        else:
            out.append(piece)
    return out


def is_range(m):
    """00-99 is a range. 2025-05 is a year and a month, not a range."""
    a, b = m.group(1), m.group(2)
    return a != b and not (len(a) == 4 and len(b) == 2 and 1 <= int(b) <= 12)


def n_words(s):
    return len(WORD.findall(s))


# ---------------------------------------------------------------- checks


def looks_like_verb(w):
    return w not in NOUNS_LIKE_VERBS and bool(VERB_END.search(w))


def check_eto(sent):
    """Return a hint if the sentence is a definition "X это Y" with no dash."""
    ws = re.findall(r"\S+", sent)
    low = [w.strip(".,:;!?()«»\"—–-").lower() for w in ws]
    if not low or low[0] in ETO_SKIP_FIRST:
        return None
    for k in range(1, min(len(ws) - 1, 7)):
        if low[k] != "это":
            continue
        prev, nxt = ws[k - 1], low[k + 1]
        if any(w[-1] in ",:;" for w in ws[:k]):  # a clause before "это": not a simple definition
            return None
        if prev[-1] in "—–-(«\"" or not low[k - 1] or low[k - 1] in NO_DASH_BEFORE_ETO:
            return None
        if looks_like_verb(low[k - 1]) or looks_like_verb(nxt) or nxt in ETO_SKIP_NEXT:
            return None
        if re.search(r"[^е]ее$", nxt):  # comparative: «это труднее»
            return None
        return f"«{prev} — это {ws[k + 1]}»"
    return None


def check_text(path, text, calques, bans, pairs=()):
    out = []

    def add(line, level, rule, msg, ctx=""):
        out.append(Finding(path, line, level, rule, msg, ctx))

    for no, unit, kind in prose_units(text):
        # --- typography
        if '"' in unit:
            add(no, "ERROR", "quotes", "Прямые кавычки в тексте. Используйте «ёлочки».", unit)
        if re.search(r"(?<!-)--(?!-)", unit):
            add(no, "ERROR", "double-hyphen", 'Два дефиса "--". Используйте тире «—» или перестройте фразу.', unit)
        if re.search(r"\s-\s", unit):
            add(no, "WARN", "hyphen-as-dash", "Дефис с пробелами вместо тире «—».", unit)
        for m in RANGE.finditer(unit):
            if is_range(m):
                add(no, "WARN", "range-hyphen", f"Диапазон «{m.group(0)}»: нужно короткое тире «{m.group(1)}–{m.group(2)}».", unit)
        if re.search(r"(->|=>|→|⇒)", unit):
            add(no, "WARN", "arrow", "Стрелка в тексте. Напишите словами.", unit)
        if re.search(r"[А-Яа-яЁё] {2,}[А-Яа-яЁё]", unit):
            add(no, "WARN", "double-space", "Двойной пробел.", unit)
        for m in re.finditer(r"(?<![\w.,])(\d+)\.(\d+)(?!\w|\.\d)", unit):
            if m.group(1) != "0" and len(m.group(2)) < 2:  # 5.1, 9.3: a version or a chapter number
                continue
            before = unit[: m.start()].rstrip(" («")
            if not DOT_OK_BEFORE.search(before):
                add(no, "WARN", "decimal-point", f"«{m.group(0)}»: в тексте пишем запятую ({m.group(0).replace('.', ',')}). Версии и номера глав не трогаем.", unit)
        m = re.search(r"(?<![\w-])([А-Яа-яЁё]{2,})\s+\1(?![\w-])", unit, re.I)
        if m:
            add(no, "WARN", "doubled-word", f"Слово повторено: «{m.group(0)}».", unit)
        for rx, good in YO_WORDS:
            m = rx.search(unit)
            if m:
                add(no, "WARN", "yo", f"«{m.group(0)}»: пишем с «ё» ({good}).", unit)

        # --- missing dash before «это»
        sents = split_sentences(unit)
        for s in sents:
            hint = check_eto(s)
            if hint:
                add(no, "WARN", "dash-before-eto", f"Возможно, нужно тире: {hint}.", s)

        # --- calques, stop words
        for rx, fix, level, why in calques:
            m = rx.search(unit)
            if m:
                add(no, level, "calque", f"«{m.group(0)}» → {fix}" + (f" ({why})" if why else ""), unit)

        # --- glossary: banned spelling of a term
        for rx, good in bans:
            m = rx.search(unit)
            if m:
                add(no, "ERROR", "glossary", f"«{m.group(0)}» нельзя. В глоссарии: {good}.", unit)

        # --- flow
        counts = [n_words(s) for s in sents]
        for s, n in zip(sents, counts):
            if n > MAX_WORDS:
                add(no, "WARN", "long-sentence", f"Предложение из {n} слов. Разбейте на 2–3.", s)
        firsts = [(WORD.findall(s) or [""])[0].lower() for s in sents]
        for k in range(len(firsts) - 2):
            if len(firsts[k]) > 2 and firsts[k] == firsts[k + 1] == firsts[k + 2]:
                add(no, "WARN", "same-opener", f"Три предложения подряд начинаются с «{firsts[k]}». Измените ритм.", unit)
                break
        if kind == "p" and not NAV.match(unit):
            run = best = 0
            for n in counts:
                run = run + 1 if n <= CHOPPY_WORDS else 0
                best = max(best, run)
            if best >= CHOPPY_RUN:
                add(no, "WARN", "choppy", f"{best} коротких предложений подряд (до {CHOPPY_WORDS} слов). Свяжите их: «поэтому», «но», «то есть».", unit)

    # --- term drift: the Russian and the English form of one term on the same page
    if pairs:
        units = list(prose_units(text, keep_code=True))
        for ru, en in pairs:
            rx_ru = re.compile(r"(?<![\w-])" + re.escape(ru) + r"[а-яё]*", re.I)
            rx_en = re.compile(r"(?<![\w-])" + re.escape(en) + r"(?:e?s)?(?![\w-])", re.I)
            hits_ru = [(no, m.group(0)) for no, u, _ in units for m in rx_ru.finditer(u)]
            hits_en = [(no, m.group(0)) for no, u, _ in units for m in rx_en.finditer(u) if not m.group(0).isupper()]
            if len(hits_ru) >= 3 and len(hits_en) >= 3:
                minor = hits_ru if len(hits_ru) <= len(hits_en) else hits_en
                add(minor[0][0], "WARN", "term-drift",
                    f"На странице есть и «{hits_ru[0][1]}» ({len(hits_ru)}), и «{hits_en[0][1]}» ({len(hits_en)}). Выберите одну форму по глоссарию.")
    out.sort(key=lambda f: f.line)
    return out


# ---------------------------------------------------------------- stats


def stats(text):
    counts, links, runs = [], 0, 0
    for _, unit, kind in prose_units(text):
        if kind != "p" or NAV.match(unit):
            continue
        c = [n_words(s) for s in split_sentences(unit)]
        c = [n for n in c if n]
        counts += c
        links += len(LINK_WORDS.findall(unit))
        run = best = 0
        for n in c:
            run = run + 1 if n <= CHOPPY_WORDS else 0
            best = max(best, run)
        runs += best >= CHOPPY_RUN
    if not counts:
        return None
    return {
        "sentences": len(counts),
        "median": statistics.median(counts),
        "short": 100 * sum(n <= SHORT_WORDS for n in counts) / len(counts),
        "links": 100 * links / len(counts),
        "choppy": runs,
    }


def print_stats(files):
    print(f"{'median':>6} {'short%':>6} {'links':>5} {'choppy':>6}  file   (target: median >= {TARGET_MEDIAN}, short <= {TARGET_SHORT}%, links >= {TARGET_LINKS} per 100 sentences)")
    for f in files:
        st = stats(f.read_text(encoding="utf-8"))
        if not st:
            continue
        bad = []
        if st["median"] < TARGET_MEDIAN:
            bad.append("median")
        if st["short"] > TARGET_SHORT:
            bad.append("short")
        if st["links"] < TARGET_LINKS:
            bad.append("links")
        mark = "ok" if not bad else "LOW: " + ", ".join(bad)
        print(f"{st['median']:6.1f} {st['short']:6.0f} {st['links']:5.0f} {st['choppy']:6d}  {f}  [{mark}]")


# ---------------------------------------------------------------- guard (--before)


def parts(text):
    front, code, inline, links, heads, nums, words = [], [], Counter(), Counter(), [], Counter(), 0
    block = None
    for i, raw, kind in classify(text):
        if kind == "front":
            front.append(raw)
        elif kind == "code":
            if block is None:
                block = []
            block.append(raw)
            continue
        if block is not None:
            code.append("\n".join(block))
            block = None
        if kind in ("prose", "table", "heading"):
            inline.update(re.findall(r"`[^`]*`", raw))
            links.update(re.findall(r"\]\(([^)]*)\)", raw))
            c = clean(raw)
            nums.update(re.findall(r"\d+", c))
            words += n_words(c)
            if kind == "heading":
                heads.append(re.match(r"\s*(#+)", raw).group(1))
    if block is not None:
        code.append("\n".join(block))
    return {"front": front, "code": code, "inline": inline, "links": links, "heads": heads, "nums": nums, "words": words}


def guard(path, old, new, max_change):
    a, b = parts(old), parts(new)
    out = []

    def add(level, rule, msg):
        out.append(Finding(path, 0, level, rule, msg))

    def delta(x, y):
        gone, came = x - y, y - x
        return f"пропало: {sorted(gone.elements())[:6]}, появилось: {sorted(came.elements())[:6]}"

    if a["front"] != b["front"]:
        add("ERROR", "front-matter-changed", "Front matter изменился.")
    if a["code"] != b["code"]:
        add("ERROR", "code-changed", f"Блоки кода изменились (было {len(a['code'])}, стало {len(b['code'])}).")
    if a["inline"] != b["inline"]:
        add("ERROR", "inline-code-changed", "Изменился код в обратных кавычках: " + delta(a["inline"], b["inline"]))
    if a["links"] != b["links"]:
        add("ERROR", "link-changed", "Изменились ссылки или пути картинок: " + delta(a["links"], b["links"]))
    if a["heads"] != b["heads"]:
        add("ERROR", "heading-changed", f"Изменилась структура заголовков (было {len(a['heads'])}, стало {len(b['heads'])}).")
    if a["nums"] != b["nums"]:
        add("ERROR", "number-changed", "Изменились числа в тексте: " + delta(a["nums"], b["nums"]))
    if old.count("\n") != new.count("\n"):
        add("WARN", "line-count", f"Число строк изменилось: {old.count(chr(10)) + 1} → {new.count(chr(10)) + 1}. compare.py нужны одинаковые строки.")
    change = 100 * (b["words"] - a["words"]) / max(a["words"], 1)
    if abs(change) > max_change:
        add("WARN", "length", f"Длина текста изменилась на {change:+.1f}% (лимит {max_change}%).")
    return out, change


# ---------------------------------------------------------------- fix (--fix)


def split_protected(raw):
    """Yield (segment, is_text). Inline code, link targets, URLs, tags and {…} are not text."""
    pos = 0
    for m in PROTECTED.finditer(raw):
        yield raw[pos : m.start()], True
        yield m.group(0), False
        pos = m.end()
    yield raw[pos:], True


def fix_line(raw):
    """Fix number ranges and straight quotes in one prose line. Protected spans are not touched."""
    segs = [
        (RANGE.sub(lambda m: f"{m.group(1)}–{m.group(2)}" if is_range(m) else m.group(0), s), t) if t else (s, t)
        for s, t in split_protected(raw)
    ]
    line = "".join(s for s, _ in segs)
    flat = "".join(s if t else "\x00" * len(s) for s, t in segs)  # protected spans masked, same length
    idx = [i for i, ch in enumerate(flat) if ch == '"']
    if not idx or len(idx) % 2:
        return line
    # Leave risky lines for a human: nested quotes, JSON-like text, quotes inside tags.
    if "«" in flat or re.search(r'[={\\]"|"\s*[:}]', line):
        return line
    if any('"' in s for s, t in segs if not t and not s.startswith("`")):
        return line
    for k, i in enumerate(idx):
        prev_ch = flat[i - 1] if i else " "
        next_ch = flat[i + 1] if i + 1 < len(flat) else " "
        if k % 2 == 0:  # opening quote
            if prev_ch not in " \t(—–-/|*_[>" or next_ch.isspace():
                return line
        else:  # closing quote
            if prev_ch.isspace() or next_ch not in " \t.,;:!?)—–-/|*_]<\x00":
                return line
    chars = list(line)
    for k, i in enumerate(idx):
        chars[i] = "«" if k % 2 == 0 else "»"
    return "".join(chars)


def fix_text(text):
    """Headings are skipped: a changed heading changes its anchor."""
    lines = text.split("\n")
    changed = 0
    for i, raw, kind in classify(text):
        if kind in ("prose", "table"):
            fixed = fix_line(raw)
            if fixed != raw:
                lines[i] = fixed
                changed += 1
    return "\n".join(lines), changed


# ---------------------------------------------------------------- main


def iter_files(paths):
    for p in paths:
        p = Path(p)
        if p.is_dir():
            yield from sorted(list(p.rglob("*.md")) + list(p.rglob("*.mdx")))
        else:
            yield p


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--strict", action="store_true", help="exit 1 on WARN too")
    ap.add_argument("--glossary", help="glossary.md with an optional «Не писать» column")
    ap.add_argument("--summary", action="store_true", help="print only counts per rule")
    ap.add_argument("--only", help="comma-separated rule names to show")
    ap.add_argument("--stats", action="store_true", help="print rhythm numbers per file")
    ap.add_argument("--before", help="old version of the file: check that code, links, numbers did not change")
    ap.add_argument("--max-change", type=float, default=5.0, help="allowed length change in %% for --before (default 5)")
    ap.add_argument("--fix", action="store_true", help="fix straight quotes and number ranges in place")
    a = ap.parse_args()
    files = list(iter_files(a.paths))

    if a.stats:
        print_stats(files)
        return

    if a.before:
        if len(files) != 1:
            sys.exit("--before needs exactly one file")
        old = Path(a.before).read_text(encoding="utf-8")
        new = files[0].read_text(encoding="utf-8")
        findings, change = guard(str(files[0]), old, new, a.max_change)
        for x in findings:
            print(x)
        errs = sum(1 for x in findings if x.level == "ERROR")
        print(f"-- guard: {errs} error, {len(findings) - errs} warn, length {change:+.1f}%", file=sys.stderr)
        sys.exit(1 if errs or (a.strict and findings) else 0)

    if a.fix:
        total = 0
        for f in files:
            old = f.read_text(encoding="utf-8")
            new, changed = fix_text(old)
            if not changed:
                continue
            problems = [x for x in guard(str(f), old, new, 100)[0] if x.level == "ERROR"]
            if problems:
                print(f"{f}: not fixed, the guard failed: {problems[0].msg}")
                continue
            f.write_text(new, encoding="utf-8")
            total += changed
            print(f"{f}: fixed {changed} lines")
        print(f"-- fixed {total} lines", file=sys.stderr)
        return

    calques = load_calques()
    pairs = load_term_pairs()
    bans = load_glossary_bans(a.glossary)
    only = set(a.only.split(",")) if a.only else None
    findings = []
    for f in files:
        findings += check_text(str(f), f.read_text(encoding="utf-8"), calques, bans, pairs)
    if only:
        findings = [x for x in findings if x.rule in only]

    if a.summary:
        c = Counter((x.level, x.rule) for x in findings)
        for (lvl, rule), n in sorted(c.items(), key=lambda kv: -kv[1]):
            print(f"{n:5d}  {lvl:5s}  {rule}")
    else:
        for x in findings:
            print(x)
    errs = sum(1 for x in findings if x.level == "ERROR")
    print(f"-- {errs} error, {len(findings) - errs} warn", file=sys.stderr)
    sys.exit(1 if errs or (a.strict and len(findings) > errs) else 0)


if __name__ == "__main__":
    main()
