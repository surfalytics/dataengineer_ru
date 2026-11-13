"""Глава 5: структурированный вывод (JSON). Разбор, проверка по схеме, повтор при ошибке.
Модель здесь не настоящая: mock_llm() ломает формат ответа с заданными вероятностями.
В настоящей системе вы замените mock_llm() вызовом API модели, остальной код останется тем же.
Что показывает:
 1. типичные поломки: JSON внутри блока кода с тройными обратными кавычками, вступление, дробное число, нет ключа, лишняя запятая, число вне шкалы;
 2. три режима: строгий разбор, терпимый разбор, терпимый разбор + проверка + повтор с описанием ошибки;
 3. цену повторов: сколько вызовов модели приходится на один запрос.
Запуск: python3 -I scripts/ai-engineering-code/ch05_structured_output.py   (только стандартная библиотека)"""
import json
import random
import re
from collections import Counter

# Схема ответа: score целое от 1 до 5, reason строка. Её же мы описываем в prompt.
PROMPT = ("Оцени ответ по шкале от 1 до 5. Верни только JSON с ключами score (целое число) и reason (строка).\n"
          "Ответ для оценки: {answer}")

FENCE = "`" * 3  # тройные обратные кавычки: так модели часто оборачивают код

BASE = [("ok", .55), ("fenced", .12), ("preamble", .10), ("fraction", .08),
        ("missing_key", .05), ("trailing_comma", .05), ("out_of_range", .05)]
AFTER_FEEDBACK = [("ok", .92), ("fenced", .03), ("preamble", .02), ("fraction", .01),
                  ("missing_key", .01), ("trailing_comma", .005), ("out_of_range", .005)]


def mock_llm(prompt, rng, truth):
    """Игрушечная модель: знает верную оценку, но иногда ломает формат.
    После описания ошибки в prompt (слово «Исправь») ломает формат реже."""
    table = AFTER_FEEDBACK if "Исправь" in prompt else BASE
    kind = rng.choices([k for k, _ in table], weights=[w for _, w in table])[0]
    score, reason = truth
    good = json.dumps({"score": score, "reason": reason}, ensure_ascii=False)
    return {
        "ok": good,
        "fenced": f"{FENCE}json\n{good}\n{FENCE}",
        "preamble": f"Конечно! Вот оценка: {good}\nНадеюсь, это поможет.",
        "fraction": json.dumps({"score": score + 0.5, "reason": reason}, ensure_ascii=False),
        "missing_key": json.dumps({"score": score}),
        "trailing_comma": good[:-1] + ",}",
        "out_of_range": json.dumps({"score": score + 5, "reason": reason}, ensure_ascii=False),
    }[kind]


def validate(obj):
    """Проверка по схеме. Возвращает список ошибок, пустой список значит всё хорошо."""
    if not isinstance(obj, dict):
        return ["ответ не JSON-объект"]
    errors = [f"нет ключа {k}" for k in ("score", "reason") if k not in obj]
    if "score" in obj:
        s = obj["score"]
        if isinstance(s, bool) or not isinstance(s, int):
            errors.append("score должен быть целым числом")
        elif not 1 <= s <= 5:
            errors.append("score вне диапазона 1..5")
    if "reason" in obj and not isinstance(obj["reason"], str):
        errors.append("reason должен быть строкой")
    return errors


def strict_parse(text):
    try:
        return json.loads(text), []
    except json.JSONDecodeError as e:
        return None, [f"это не JSON ({e.msg})"]


def tolerant_parse(text):
    """Достаём JSON из обёртки, чиним лишнюю запятую, потом проверяем по схеме."""
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        return None, ["в ответе нет JSON-объекта"]
    chunk = re.sub(r",\s*}", "}", text[start:end + 1])
    try:
        obj = json.loads(chunk)
    except json.JSONDecodeError as e:
        return None, [f"это не JSON ({e.msg})"]
    return obj, validate(obj)


def ask(i, mode, max_retries=3, trace=None):
    """Один запрос в режиме mode. Возвращает (успех, число вызовов модели)."""
    truth = (1 + i % 5, "ответ полный и по делу")
    prompt = PROMPT.format(answer=f"пример №{i}")
    for attempt in range(max_retries + 1 if mode == "retry" else 1):
        rng = random.Random(f"{i}-{attempt}")
        raw = mock_llm(prompt, rng, truth)
        obj, errors = strict_parse(raw) if mode == "strict" else tolerant_parse(raw)
        if mode == "strict" and obj is not None:
            errors = validate(obj)
        if trace is not None:
            trace.append((attempt + 1, raw, errors))
        if not errors:
            return True, attempt + 1
        prompt = (PROMPT.format(answer=f"пример №{i}")
                  + f"\n\nПредыдущий ответ не прошёл проверку: {'; '.join(errors)}. Исправь и верни только JSON.")
    return False, attempt + 1


N = 2000
print("== 1. Три режима на", N, "запросах")
print("режим                                   | успех  | вызовов на запрос")
for mode, title in [("strict", "строгий json.loads, без повтора"),
                    ("tolerant", "терпимый разбор, без повтора"),
                    ("retry", "терпимый разбор + повтор (до 3)")]:
    results = [ask(i, mode) for i in range(N)]
    ok = sum(r[0] for r in results)
    calls = sum(r[1] for r in results)
    print(f"{title:<40}| {ok / N:5.1%} | {calls / N:.2f}")

print("\n== 2. Что ломается с первого раза (первый ответ модели)")
kinds = Counter()
for i in range(N):
    trace = []
    ask(i, "tolerant", trace=trace)
    errs = trace[0][2]
    kinds["без ошибок после терпимого разбора" if not errs else errs[0]] += 1
for k, v in kinds.most_common():
    print(f"{v / N:6.1%}  {k}")

print("\n== 3. Пример запроса с повтором")
for i in range(N):
    trace = []
    ok, calls = ask(i, "retry", trace=trace)
    if calls > 1:
        for n, raw, errors in trace:
            print(f"попытка {n}: {raw!r}")
            print("  проверка:", errors or "ok")
        break
