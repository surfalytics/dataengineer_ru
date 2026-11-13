#!/usr/bin/env python3
"""Глава 8: проверка синтетических данных, мини-версия пайплайна Llama 3 для кода. Без внешних библиотек.

Что показывает скрипт:
  1. «Модель» (mock_solve) пишет решения задач. Часть решений с ошибками: синтаксис, лишнее имя, логика.
  2. Три проверки подряд: parser (ast.parse), мини-linter (неизвестные имена), unit tests.
  3. Repair: упавшее решение отправляем модели вместе с текстом ошибки. Прошло проверки: оставляем.
  4. Back-translation: из кода пишем объяснение, из объяснения снова код. Объяснение берём в датасет,
     только если код из него проходит те же тесты.
В реальном проекте mock_solve / mock_explain / mock_from_text заменяются вызовами LLM.
Запуск из корня репозитория: python3 -I scripts/ai-engineering-code/ch08_synth_verify.py
"""
import ast
import builtins
import random

rng = random.Random(3)

# ---------- Задачи: описание, верное решение, три типа ошибок, тесты ----------
TASKS = {
    "sum_even": dict(
        ok="def sum_even(xs):\n    return sum(x for x in xs if x % 2 == 0)",
        syntax="def sum_even(xs)\n    return sum(x for x in xs if x % 2 == 0)",
        name="def sum_even(xs):\n    return total + sum(x for x in xs if x % 2 == 0)",
        logic="def sum_even(xs):\n    return sum(x for x in xs if x % 2 == 1)",
        tests=[(([1, 2, 3, 4],), 6), (([],), 0), (([7],), 0)],
        says="возвращает сумму чётных чисел списка", wrong_says="возвращает сумму нечётных чисел списка"),
    "dedup": dict(
        ok="def dedup(xs):\n    seen = set()\n    out = []\n    for x in xs:\n        if x not in seen:\n            seen.add(x)\n            out.append(x)\n    return out",
        syntax="def dedup(xs):\n    seen = set(\n    return list(seen)",
        name="def dedup(xs):\n    out = []\n    for x in xs:\n        if x not in seen:\n            out.append(x)\n    return out",
        logic="def dedup(xs):\n    return sorted(set(xs))",
        tests=[(([3, 1, 3, 2, 1],), [3, 1, 2]), (([],), [])],
        says="убирает повторы и сохраняет порядок первого появления", wrong_says="сортирует элементы и убирает повторы"),
    "top_key": dict(
        ok="def top_key(d):\n    return max(d, key=d.get)",
        syntax="def top_key(d):\n    return max(d, key=d.get",
        name="def top_key(d):\n    return max(d, key=values.get)",
        logic="def top_key(d):\n    return min(d, key=d.get)",
        tests=[(({"a": 1, "b": 5, "c": 2},), "b"), (({"x": 9},), "x")],
        says="возвращает ключ с наибольшим значением", wrong_says="возвращает ключ с наименьшим значением"),
    "is_palindrome": dict(
        ok="def is_palindrome(s):\n    t = ''.join(c.lower() for c in s if c.isalnum())\n    return t == t[::-1]",
        syntax="def is_palindrome(s):\n    t = ''.join(c.lower() for c in s if c.isalnum()\n    return t == t[::-1]",
        name="def is_palindrome(s):\n    return t == t[::-1]",
        logic="def is_palindrome(s):\n    return s == s[::-1]",
        tests=[(("А роза упала на лапу Азора",), True), (("abc",), False), (("Madam",), True)],
        says="проверяет, читается ли строка одинаково в обе стороны, без учёта регистра и пробелов",
        wrong_says="проверяет, что строка совпадает со своим отражением, учитывая регистр"),
    "median": dict(
        ok="def median(xs):\n    s = sorted(xs)\n    n = len(s)\n    m = n // 2\n    return s[m] if n % 2 else (s[m - 1] + s[m]) / 2",
        syntax="def median(xs):\n    s = sorted(xs)\n    return s[len(s) // 2",
        name="def median(xs):\n    n = len(s)\n    return s[n // 2]",
        logic="def median(xs):\n    n = len(xs)\n    m = n // 2\n    return xs[m] if n % 2 else (xs[m - 1] + xs[m]) / 2",
        tests=[(([5, 1, 3],), 3), (([4, 1, 3, 2],), 2.5)],
        says="возвращает медиану чисел", wrong_says="возвращает середину списка в исходном порядке"),
    "clamp": dict(
        ok="def clamp(x, lo, hi):\n    return max(lo, min(x, hi))",
        syntax="def clamp(x, lo, hi):\n    return max(lo, min(x, hi)",
        name="def clamp(x, lo, hi):\n    return max(low, min(x, hi))",
        logic="def clamp(x, lo, hi):\n    return min(lo, max(x, hi))",
        tests=[((5, 0, 3), 3), ((-1, 0, 3), 0), ((2, 0, 3), 2)],
        says="ограничивает число диапазоном от lo до hi", wrong_says="возвращает меньшее из lo и x"),
    "word_count": dict(
        ok="def word_count(text):\n    out = {}\n    for w in text.lower().split():\n        out[w] = out.get(w, 0) + 1\n    return out",
        syntax="def word_count(text):\n    out = {}\n    for w in text.lower().split()\n        out[w] = out.get(w, 0) + 1\n    return out",
        name="def word_count(text):\n    for w in text.lower().split():\n        out[w] = out.get(w, 0) + 1\n    return out",
        logic="def word_count(text):\n    out = {}\n    for w in text.split():\n        out[w] = out.get(w, 0) + 1\n    return out",
        tests=[(("Да нет да",), {"да": 2, "нет": 1})],
        says="считает слова без учёта регистра", wrong_says="считает слова с учётом регистра"),
    "chunks": dict(
        ok="def chunks(xs, n):\n    return [xs[i:i + n] for i in range(0, len(xs), n)]",
        syntax="def chunks(xs, n):\n    return [xs[i:i + n] for i in range(0, len(xs), n)",
        name="def chunks(xs, n):\n    return [xs[i:i + size] for i in range(0, len(xs), n)]",
        logic="def chunks(xs, n):\n    return [xs[i:i + n] for i in range(0, len(xs) - n, n)]",
        tests=[(([1, 2, 3, 4, 5], 2), [[1, 2], [3, 4], [5]]), (([], 3), [])],
        says="режет список на куски по n элементов", wrong_says="режет список на куски и отбрасывает последний неполный кусок"),
}
KINDS = ["syntax", "name", "logic"]


# ---------- Игрушечные «модели» ----------
def mock_solve(task, feedback=None):
    p_ok = 0.8 if feedback else 0.55          # с подсказкой об ошибке модель чаще попадает
    return TASKS[task]["ok"] if rng.random() < p_ok else TASKS[task][rng.choice(KINDS)]


def mock_explain(task):
    return TASKS[task]["says"] if rng.random() > 0.15 else TASKS[task]["wrong_says"]


def mock_from_text(task, text):
    return TASKS[task]["ok"] if text == TASKS[task]["says"] else TASKS[task]["logic"]


# ---------- Проверки ----------
def check_parser(code):
    try:
        ast.parse(code)
        return None
    except SyntaxError as e:
        return f"SyntaxError: {e.msg} (строка {e.lineno})"


def check_linter(code):
    """Мини-linter: имена, которые читаем, но нигде не определили."""
    tree = ast.parse(code)
    defined = set(dir(builtins))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            defined.add(node.name)
            defined.update(a.arg for a in node.args.args)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            defined.add(node.id)
    missing = sorted({n.id for n in ast.walk(tree)
                      if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and n.id not in defined})
    return f"NameError: имя {missing[0]!r} не определено" if missing else None


def check_tests(task, code):
    ns = {}
    try:
        exec(code, ns)       # код здесь наш, игрушечный. Настоящий код от модели запускайте в sandbox
        fn = ns[task]
        for args, expected in TASKS[task]["tests"]:
            got = fn(*args)
            if got != expected:
                return f"AssertionError: {fn.__name__}{args} вернул {got!r}, ожидали {expected!r}"
    except Exception as e:
        return f"{type(e).__name__}: {e}"
    return None


def verify(task, code):
    return check_parser(code) or check_linter(code) or check_tests(task, code)


# ---------- Пайплайн ----------
SAMPLES_PER_TASK = 10
stats = {"сгенерировано": 0, "упало на parser": 0, "упало на linter": 0, "упало на тестах": 0,
         "исправлено после repair": 0, "отброшено после repair": 0}
kept, shown = [], []
for task in TASKS:
    for _ in range(SAMPLES_PER_TASK):
        stats["сгенерировано"] += 1
        code = mock_solve(task)
        err = check_parser(code)
        if err:
            stats["упало на parser"] += 1
        elif (err := check_linter(code)):
            stats["упало на linter"] += 1
        elif (err := check_tests(task, code)):
            stats["упало на тестах"] += 1
        if err is None:
            kept.append((task, code))
            continue
        if len(shown) < 3:
            shown.append(err)
        fixed = mock_solve(task, feedback=err)               # repair: промпт содержит ошибку
        if verify(task, fixed) is None:
            stats["исправлено после repair"] += 1
            kept.append((task, fixed))
        else:
            stats["отброшено после repair"] += 1

print("=== Проверка кода: parser, linter, unit tests, repair ===")
for k, v in stats.items():
    print(f"  {k}: {v}")
print(f"Попало в SFT-датасет: {len(kept)} из {stats['сгенерировано']}")
print("Примеры текста ошибки, который уходит модели при repair:")
for s in shown:
    print("  -", s)

print("\n=== Back-translation: код -> объяснение -> код ===")
explained = accepted = 0
for task, code in kept:
    text = mock_explain(task)
    explained += 1
    back = mock_from_text(task, text)
    if check_tests(task, back) is None:      # код из объяснения проходит те же тесты
        accepted += 1
print(f"Объяснений написано: {explained}, принято: {accepted}, отброшено: {explained - accepted}")
print("Принятые объяснения проверены косвенно: по ним можно восстановить рабочий код.")
