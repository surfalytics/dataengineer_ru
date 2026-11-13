"""Глава 2: structured outputs. Игрушечная «модель» выдаёт токены JSON. Сравниваем обычный sampling и constrained sampling
(маска logits по грамматике), смотрим, что делает обрыв по лимиту токенов, и чиним JSON защитным парсером (post-processing).
Настоящая модель заменит функцию toy_logits. Идея маски logits та же, что у outlines, guidance и llama.cpp.
Запуск: python3 -I scripts/ai-engineering-code/ch02_structured_output.py   (только стандартная библиотека)"""
import json
import math
import random
import re

rng = random.Random(11)
STRINGS = ['"Заказ готов"', '"Скоро увидимся"', '"Спасибо за покупку"']
VOCAB = ["{", "}", '"title"', '"body"', ":", ","] + STRINGS + ["[", "]", "null"]
# грамматика: что можно на каждом шаге для документа {"title": <строка>, "body": <строка>}
GRAMMAR = [{"{"}, {'"title"'}, {":"}, set(STRINGS), {","}, {'"body"'}, {":"}, set(STRINGS), {"}"}]
BONUS = 7  # насколько «знает формат» игрушечная модель


def toy_logits(step):
    """Правильным токенам даём бонус, ко всем добавляем шум: модель обычно права, но иногда ошибается."""
    return [(BONUS if tok in GRAMMAR[step] else 0.0) + rng.gauss(0, 1.5) for tok in VOCAB]


def softmax(logits):
    m = max(logits)
    e = [math.exp(x - m) for x in logits]
    s = sum(e)
    return [x / s for x in e]


def generate(constrained, max_tokens=9):
    out = []
    for step in range(max_tokens):
        logits = toy_logits(step)
        if constrained:  # constrained sampling: запрещённым токенам -inf, после softmax их вероятность равна 0
            logits = [x if VOCAB[i] in GRAMMAR[step] else float("-inf") for i, x in enumerate(logits)]
        out.append(VOCAB[rng.choices(range(len(VOCAB)), weights=softmax(logits))[0]])
    return "".join(out)


def is_valid(text):
    try:
        d = json.loads(text)
        return isinstance(d, dict) and set(d) == {"title", "body"}
    except json.JSONDecodeError:
        return False


def repair(text):
    """Защитный парсер: закрывает строку и скобки, дописывает null после «:», убирает лишние запятые."""
    stack, in_str, esc = [], False, False
    for ch in text:
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
        elif ch in "{[":
            stack.append("}" if ch == "{" else "]")
        elif ch in "}]" and stack:
            stack.pop()
    fixed = text + ('"' if in_str else "")
    fixed = fixed.rstrip()
    if fixed.endswith(":"):
        fixed += "null"
    fixed = fixed.rstrip(",")
    fixed = re.sub(r",\s*([}\]])", r"\1", fixed)
    return fixed + "".join(reversed(stack))


N = 2000
print("== 1. Обычный sampling и constrained sampling (2000 запусков по 9 токенов)")
for name, flag in [("обычный sampling", False), ("constrained sampling", True)]:
    ok = sum(is_valid(generate(flag)) for _ in range(N))
    print(f"{name:21s} валидный JSON с нужными ключами: {ok / N:6.1%}")

print("\n== 2. Constrained sampling гарантирует формат, а не смысл")
for _ in range(3):
    print(generate(True))

print("\n== 3. Обрыв по лимиту токенов (max_tokens = 7 вместо 9)")
for name, flag in [("обычный sampling", False), ("constrained sampling", True)]:
    ok = sum(is_valid(generate(flag, 7)) for _ in range(N))
    print(f"{name:21s} валидный JSON: {ok / N:6.1%}")
cut = generate(True, 7)
print("пример обрыва:      ", cut)
print("после repair():     ", repair(cut), "| валидный:", is_valid(repair(cut)))
fixed = sum(is_valid(repair(generate(True, 7))) for _ in range(N))
print(f"repair() делает обрезанный ответ валидным в {fixed / N:.0%} случаев, но в body лежит null: содержимое потеряно")

print("\n== 4. Защитный парсер на типичных ошибках")
broken = ['{"title": "Привет", "body": "Мир"', '{"title": "Привет", "body": "Мир', '{"title": "Привет", "body": "Мир",}', '{"title": "Привет", "body":']
for text in broken:
    fixed_text = repair(text)
    print(f"{text!r:50s} -> {fixed_text!r}  валидный: {is_valid(fixed_text)}")

print("\n== 5. Формат тоже стоит токенов: JSON и YAML для одних данных")
j = '{"title": "Заказ готов", "body": "Скоро увидимся"}'
y = "title: Заказ готов\nbody: Скоро увидимся"
print(f"JSON: {len(j)} символов, служебных знаков {len(re.findall(r'[{}\":,]', j))}; YAML: {len(y)} символов, служебных знаков {len(re.findall(r'[:]', y))}")
print("меньше служебных знаков -> меньше токенов на ответ (так рассуждали в LinkedIn)")
