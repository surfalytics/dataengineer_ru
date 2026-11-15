#!/usr/bin/env python3
"""Глава 15 (этап Empathy): оценка проблемных интервью и сводная таблица по опросу.
Только стандартная библиотека. Запуск: python3 -I ch15_interviews.py"""
from collections import Counter, defaultdict

# --- 1. Оценка проблемного интервью (шкала из книги: максимум 43 балла) ---
# Для каждого вопроса: баллы за ответ "да" / "отчасти" / "нет".
WEIGHTS = {
    "ранжировал проблемы":       (10, 5, 0),
    "уже решает проблему":       (10, 5, 0),
    "был вовлечён":              (8, 4, 0),
    "согласен на вторую встречу": (8, 4, 0),
    "дал контакты других":       (4, 2, 0),
    "предложил заплатить":       (3, 1, 0),
}
ANSWER = {"да": 0, "отчасти": 1, "нет": 2}
GOOD = 31  # 31 и выше: хорошее интервью

# Наши выдуманные интервью: ответы по шести вопросам и проблема на первом месте.
interviews = [
    ("Анна",   "да да да да отчасти нет",           "ручная сверка"),
    ("Борис",  "да отчасти да отчасти да нет",      "ручная сверка"),
    ("Вера",   "отчасти нет отчасти нет нет нет",   "долгие отчёты"),
    ("Глеб",   "да да отчасти да да отчасти",       "ручная сверка"),
    ("Дина",   "нет отчасти отчасти отчасти нет нет", "дубли клиентов"),
]

def score(answers):
    return sum(w[ANSWER[a]] for w, a in zip(WEIGHTS.values(), answers.split()))

print("Интервью  баллы  итог")
for name, answers, _ in interviews:
    s = score(answers)
    print(f"{name:<8} {s:>6}  {'хорошее' if s >= GOOD else 'слабое'}")

good = sum(1 for _, answers, _ in interviews if score(answers) >= GOOD)
print(f"Хороших интервью: {good} из {len(interviews)}")
print("Первое место у проблемы:", dict(Counter(p for _, _, p in interviews).most_common()))

# --- 2. Сводная таблица (pivot table) по ответам опроса ---
# Наш опрос: пол, возраст и сколько часов в неделю человек слушает подкасты.
rows = [
    ("Ж", "20-30", 9), ("М", "20-30", 11), ("Ж", "20-30", 10), ("М", "30-40", 8),
    ("Ж", "30-40", 7), ("М", "30-40", 9), ("Ж", "40-50", 5), ("М", "40-50", 6),
    ("Ж", "40-50", 4), ("М", "50-60", 3), ("Ж", "50-60", 3), ("М", "50-60", 2),
]

def avg(xs):
    return sum(xs) / len(xs)

print(f"\nСреднее по всем: {avg([h for _, _, h in rows]):.2f} ч")

by_sex = defaultdict(list)
for sex, _, h in rows:
    by_sex[sex].append(h)
print("По полу:", {s: round(avg(v), 2) for s, v in sorted(by_sex.items())})

cells, by_age = defaultdict(list), defaultdict(list)
for sex, age, h in rows:
    cells[(age, sex)].append(h)
    by_age[age].append(h)
print("\nВозраст      Ж      М  Всего")
for age in sorted(by_age):
    print(f"{age:<8} {avg(cells[(age, 'Ж')]):>6.2f} {avg(cells[(age, 'М')]):>6.2f} {avg(by_age[age]):>6.2f}")
