#!/usr/bin/env python3
"""Tests for check.py. Run: python3 -I scripts/ru-proofread/test_check.py

Each case is one line of prose and the rules it must (or must not) trigger.
Add a case every time you change a regex or add a rule.
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("check", HERE / "check.py")
ck = importlib.util.module_from_spec(spec)
sys.dont_write_bytecode = True
spec.loader.exec_module(ck)

CALQUES, PAIRS = ck.load_calques(), ck.load_term_pairs()


def rules(text, bans=()):
    return {f.rule for f in ck.check_text("t.md", text, CALQUES, bans, PAIRS)}


# (text, rules that must fire, rules that must not fire)
CASES = [
    # --- dash before «это»
    ("Партиция в книге это то же, что shard.", {"dash-before-eto"}, set()),
    ("Rebalancing это перенос данных между узлами.", {"dash-before-eto"}, set()),
    ("Переменные задержки это результат компромисса.", {"dash-before-eto"}, set()),
    ("Минимальный Airflow это пять компонентов.", {"dash-before-eto"}, set()),
    ("`Asset` это виртуальная ссылка на данные.", {"dash-before-eto"}, set()),
    ("Партиция — это часть данных.", set(), {"dash-before-eto"}),
    ("Как это работает на практике?", set(), {"dash-before-eto"}),
    ("Если нагрузка неравномерна, это `skew`.", set(), {"dash-before-eto"}),
    ("Автор называет это ключом к скорости.", set(), {"dash-before-eto"}),
    ("Автор оговаривает, что в других случаях это допущение может быть неверным.", set(), {"dash-before-eto"}),
    ("Для одного DAG это работает.", set(), {"dash-before-eto"}),
    ("Чаще это атрибуты продукта.", set(), {"dash-before-eto"}),
    # --- calques and stop words
    ("Поэтому часто нужен человек в цикле.", {"calque"}, set()),
    ("Нагрузка справедливо распределена.", {"calque"}, set()),
    ("Слишком много партиций дают лишние расходы.", {"calque"}, set()),
    ("MongoDB имеет свой config server.", {"calque"}, set()),
    ("Это имеет смысл для больших таблиц.", {"calque"}, set()),
    ("Порядок имеет значение.", set(), {"calque"}),
    ("Аналитик не имеет доступа к таблице.", set(), {"calque"}),
    ("Появляется новая партиция.", set(), {"calque"}),  # «является» inside «появляется»
    ("Данные лежат в хранилище.", set(), {"calque"}),  # «данные» is not «данный»
    # --- typography
    ('Событие "данные обновились" запускает DAG.', {"quotes"}, set()),
    ("Событие «данные обновились» запускает DAG.", set(), {"quotes"}),
    ("Код `x = \"a\"` печатает строку.", set(), {"quotes"}),
    ("Добавьте число (например, 00-99) к ключу.", {"range-hyphen"}, set()),
    ("Дата 2024-01-15 в формате ISO.", set(), {"range-hyphen"}),
    ("Продажи за 2025-05 выросли.", set(), {"range-hyphen"}),  # year and month
    ("Сезон 2024-25 был лучше.", {"range-hyphen"}, set()),
    ("Узел - это сервер.", {"hyphen-as-dash"}, set()),
    ("Точность равна 0.85 на тесте.", {"decimal-point"}, set()),
    ("Точность равна 0,85 на тесте.", set(), {"decimal-point"}),
    ("Нужен Airflow 3.4 или новее, смотрите главу 5.1.", set(), {"decimal-point"}),
    ("Это еще не всё.", {"yo"}, set()),
    ("У этих счетов разные валюты.", set(), {"yo"}),  # plural «счетов» has no «ё»
    ("Проверьте, что что запрос вернул строки.", {"doubled-word"}, set()),
    # --- flow
    ("Просто. Быстро. Дёшево и надёжно. Работает везде.", {"choppy"}, set()),
    ("Rebalancing нужен при росте данных, поэтому его планируют заранее. Он нагружает сеть.", set(), {"choppy"}),
    ("Узлы хранят данные. Узлы принимают запросы. Узлы обмениваются состоянием.", {"same-opener"}, set()),
    (" ".join(["слово"] * 31) + ".", {"long-sentence"}, set()),
    ("Смотрите гл. 6 и рис. 2, там есть схема.", set(), {"choppy", "same-opener"}),
    ("Предыдущая: Глава 2. Импорт данных. Следующая: Глава 4. DuckDB и Polars.", set(), {"choppy"}),
]


def test_cases():
    bad = []
    for text, must, must_not in CASES:
        got = rules(text)
        if not must <= got or got & must_not:
            bad.append((text, f"want {sorted(must)}, not {sorted(must_not)}, got {sorted(got)}"))
    return bad


def test_skips():
    page = '---\ntitle: "Глава"\n---\n\n```python\nx = "a" -- 1\n```\n\n| A | B |\n|---|---|\n| да | нет |\n'
    return [] if not rules(page) else [("front matter, code and table separator", f"got {rules(page)}")]


def test_glossary():
    with tempfile.TemporaryDirectory() as d:
        g = Path(d) / "glossary.md"
        g.write_text(
            "| English | Как пишем | Не писать | Пояснение |\n|---|---|---|---|\n"
            "| consumer | consumer | потребитель | x |\n| DWH | хранилище данных | склад данных | x |\n",
            encoding="utf-8",
        )
        bans = ck.load_glossary_bans(g)
    bad = []
    for text, want in [
        ("Producer знает всех потребителей.", True),
        ("Новый потребитель добавляется просто.", True),
        ("Данные лежат на складе данных.", True),
        ("Потребительский спрос растёт.", False),
        ("Не надо складывать данные в одну таблицу.", False),
        ("Consumer читает события.", False),
    ]:
        if ("glossary" in rules(text, bans)) != want:
            bad.append((text, f"glossary rule should be {want}"))
    return bad


def test_term_drift():
    page = "Пайплайн читает файл. Этот пайплайн простой. Наш пайплайн готов.\n\nНовый pipeline пишет. Второй pipeline читает. Третий pipeline ждёт.\n"
    bad = [] if "term-drift" in rules(page) else [("term drift", "not found")]
    sql = "Партиция хранит день. Каждая партиция мала. Одна партиция в день.\n\nПишите `PARTITION BY`, затем `PARTITION BY` ещё раз и `PARTITION`.\n"
    if "term-drift" in rules(sql):
        bad.append(("SQL keyword PARTITION", "must not count as term drift"))
    return bad


def test_fix():
    bad = []
    for src, want in [
        ('Событие "asset обновлён" и числа 00-99.', "Событие «asset обновлён» и числа 00–99."),
        ('Код `x = "a"` и ["ссылка"](/a-1-2/) не меняются.', 'Код `x = "a"` и [«ссылка»](/a-1-2/) не меняются.'),
        ('Строка {"a": 1} остаётся.', 'Строка {"a": 1} остаётся.'),
        ('Одна " кавычка.', 'Одна " кавычка.'),
        ("| 2025-05 | 5 350 181 |", "| 2025-05 | 5 350 181 |"),
        ('Уже есть «ёлочки» и "прямые".', 'Уже есть «ёлочки» и "прямые".'),
    ]:
        got = ck.fix_line(src)
        if got != want:
            bad.append((src, f"want {want!r}, got {got!r}"))
    page = '---\ntitle: "A 1-2"\n---\n\n## Шаг "один" 1-2\n\nТекст "раз" 1-2.\n\n```\nx = "a" 1-2\n```\n'
    fixed, n = ck.fix_text(page)
    if n != 1 or 'Текст «раз» 1–2.' not in fixed or '## Шаг "один" 1-2' not in fixed or 'x = "a" 1-2' not in fixed:
        bad.append(("fix_text", "must change only the prose line"))
    return bad


def test_guard():
    old = '---\ntitle: "A"\n---\n\nТекст с `кодом` и [ссылкой](/a/). Всего 100 строк.\n\n```sql\nSELECT 1;\n```\n'
    ok = old.replace("Текст с", "Хороший текст с")
    bad = []
    if [f for f in ck.guard("t", old, ok, 50)[0] if f.level == "ERROR"]:
        bad.append(("guard", "a prose-only change must pass"))
    for name, new in [
        ("code-changed", old.replace("SELECT 1", "SELECT 2")),
        ("inline-code-changed", old.replace("`кодом`", "`кодам`")),
        ("link-changed", old.replace("(/a/)", "(/b/)")),
        ("number-changed", old.replace("100 строк", "200 строк")),
        ("front-matter-changed", old.replace('title: "A"', 'title: "B"')),
    ]:
        if name not in {f.rule for f in ck.guard("t", old, new, 50)[0]}:
            bad.append(("guard", f"{name} not found"))
    return bad


if __name__ == "__main__":
    failed = []
    for t in (test_cases, test_skips, test_glossary, test_term_drift, test_fix, test_guard):
        res = t()
        print(f"{'ok  ' if not res else 'FAIL'} {t.__name__}")
        failed += res
    for text, why in failed:
        print(f"  - {text}\n      {why}")
    sys.exit(1 if failed else 0)
