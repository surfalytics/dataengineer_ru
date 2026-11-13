"""Глава 3: functional correctness и pass@k. Запускаем код-кандидаты на unit-тестах.
Запуск: python3 scripts/ai-engineering-code/ch03_functional_correctness.py
Внимание: exec() запускает чужой код. Здесь код наш. В production запускайте код модели в песочнице."""

# Для каждой задачи: тесты и k = 3 решения от «модели» (одно-два нарочно неверные).
PROBLEMS = {
    "gcd": {
        "tests": [((15, 20), 5), ((7, 3), 1), ((12, 12), 12), ((0, 9), 9)],
        "samples": [
            "def f(a, b):\n    return min(a, b)",
            "def f(a, b):\n    while b:\n        a, b = b, a % b\n    return a",
            "def f(a, b):\n    return a * b",
        ],
    },
    "count_vowels": {
        "tests": [(("data",), 2), (("sky",), 0), (("AEIOU",), 5)],
        "samples": [
            "def f(s):\n    return sum(c in 'aeiou' for c in s)",
            "def f(s):\n    return sum(c in 'aeiou' for c in s.lower())",
            "def f(s):\n    return len(s)",
        ],
    },
    "is_sorted": {
        "tests": [(([1, 2, 3],), True), (([3, 1],), False), (([],), True), (([2, 2],), True)],
        "samples": [
            "def f(xs):\n    return xs == sorted(xs)",
            "def f(xs):\n    return all(a < b for a, b in zip(xs, xs[1:]))",
            "def f(xs):\n    return True",
        ],
    },
    "dedup_keep_order": {
        "tests": [(([3, 1, 3, 2, 1],), [3, 1, 2]), (([],), []), (([5, 5],), [5])],
        "samples": [
            "def f(xs):\n    return list(set(xs))",
            "def f(xs):\n    return sorted(set(xs))",
            "def f(xs):\n    seen = set()\n    return [x for x in xs if not (x in seen or seen.add(x))]",
        ],
    },
}


def passes(code, tests):
    ns = {}
    try:
        exec(code, ns)
        return all(ns["f"](*args) == want for args, want in tests)
    except Exception:
        return False


def pass_at_k(k):
    solved = 0
    for name, p in PROBLEMS.items():
        results = [passes(code, p["tests"]) for code in p["samples"][:k]]
        solved += any(results)
    return solved / len(PROBLEMS)


for name, p in PROBLEMS.items():
    print(f"{name:18s}", ["pass" if passes(c, p["tests"]) else "FAIL" for c in p["samples"]])
for k in (1, 2, 3):
    print(f"pass@{k} = {pass_at_k(k):.0%}")
