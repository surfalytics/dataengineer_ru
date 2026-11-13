"""Глава 3: шаблоны промптов для AI judge и симуляция его слабых мест.
Судья здесь — не настоящая модель, а простая симуляция с шумом и position bias.
В настоящей системе вы замените функцию judge_pair() на вызов LLM с промптом PAIR_PROMPT.
Запуск: python3 scripts/ai-engineering-code/ch03_judge_simulation.py   (только стандартная библиотека)"""
import random
from collections import Counter

SINGLE_PROMPT = """Дан вопрос и ответ. Оцени, насколько ответ хорош для вопроса. Шкала от 1 до 5.
- 1 значит очень плохо.
- 5 значит очень хорошо.
Вопрос: {question}
Ответ: {answer}
Оценка:"""
REFERENCE_PROMPT = """Дан вопрос, эталонный ответ и сгенерированный ответ.
Оцени, совпадает ли сгенерированный ответ с эталонным. Выведи True или False.
Вопрос: {question}
Эталонный ответ: {reference}
Сгенерированный ответ: {answer}"""
PAIR_PROMPT = """Дан вопрос и два ответа. Оцени, какой ответ лучше. Выведи A или B.
Вопрос: {question}
A: {a}
B: {b}
Лучший ответ:"""

print(PAIR_PROMPT.format(question="Что такое grain?", a="Уровень детализации строки факта.", b="Не знаю."))

# --- симуляция судьи ---
QUALITY = {"сильный ответ": 1.0, "слабый ответ": 0.0}
FIRST_BONUS = 0.6  # position bias: первая позиция получает бонус к «оценке»
NOISE = 0.8        # случайность: тот же вход может дать другой вердикт


def judge_pair(first, second, rng):
    s1 = QUALITY[first] + FIRST_BONUS + rng.gauss(0, NOISE)
    s2 = QUALITY[second] + rng.gauss(0, NOISE)
    return first if s1 >= s2 else second


rng = random.Random(7)
N = 2000

print("\n== 1. Position bias: сильный ответ стоит первым или вторым")
for order in [("сильный ответ", "слабый ответ"), ("слабый ответ", "сильный ответ")]:
    wins = sum(judge_pair(*order, rng) == "сильный ответ" for _ in range(N))
    print(f"порядок {order[0]} / {order[1]}: сильный побеждает в {wins / N:.1%}")

print("\n== 2. Лечение: судим дважды, меняя порядок")
verdicts = Counter()
for _ in range(N):
    v1 = judge_pair("сильный ответ", "слабый ответ", rng)
    v2 = judge_pair("слабый ответ", "сильный ответ", rng)
    strong = (v1 == "сильный ответ") + (v2 == "сильный ответ")
    verdicts["сильный (2 из 2)" if strong == 2 else "ничья (1 из 2)" if strong == 1 else "слабый (0 из 2)"] += 1
for k, v in verdicts.items():
    print(f"{k}: {v / N:.1%}")

print("\n== 3. Непоследовательность: один и тот же вход, 7 запусков подряд")
runs = [judge_pair("сильный ответ", "слабый ответ", rng) for _ in range(7)]
print(runs)
majority = Counter(judge_pair("сильный ответ", "слабый ответ", rng) for _ in range(5)).most_common(1)[0][0]
print("голосование по 5 запускам:", majority, "(дороже в 5 раз)")
