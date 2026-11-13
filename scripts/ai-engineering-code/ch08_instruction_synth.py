#!/usr/bin/env python3
"""Глава 8: синтез instruction data по плану тем + фильтры в стиле Self-Instruct. Без внешних библиотек.

Что показывает скрипт:
  1. План: темы x подтемы x типы инструкций. Для каждой клетки плана просим «модель» сгенерировать примеры.
  2. «Модель» здесь игрушечная (mock_teacher): она иногда повторяется, пишет слишком коротко или длинно,
     отвечает эхом на инструкцию. В реальном проекте вместо неё вызывают настоящую LLM.
  3. Фильтры: повторы, слишком короткие/длинные инструкции, одна инструкция с разными ответами,
     ответ повторяет вход. Печатаем воронку.
  4. Матрица coverage: какие клетки плана остались тонкими. Дозаполняем их вторым проходом.

Запуск из корня репозитория: python3 -I scripts/ai-engineering-code/ch08_instruction_synth.py
"""
import random
from collections import Counter, defaultdict

rng = random.Random(7)

# ---------- 1. План ----------
TOPICS = {"SQL": ["JOIN", "оконные функции", "индексы"],
          "Python": ["списки", "словари", "чтение файлов"],
          "Оркестрация": ["DAG", "retry", "backfill"],
          "Качество данных": ["тесты dbt", "дубликаты", "схема данных"]}
TYPES = {"объясни": ["Объясни простыми словами: {s}.", "Что такое {s}? Ответь кратко.", "Расскажи новичку про {s}."],
         "пример": ["Приведи пример кода для темы «{s}».", "Покажи небольшой пример: {s}.", "Напиши пример про {s}."],
         "ошибка": ["Найди типичную ошибку при работе с темой «{s}».", "Какая частая ошибка бывает в теме {s}?"],
         "сравни": ["Сравни два подхода в теме «{s}».", "Чем отличаются способы работы с темой {s}?"]}
PER_CELL = 3
cells = [(t, s, k) for t, subs in TOPICS.items() for s in subs for k in TYPES]
print(f"План: {len(TOPICS)} темы x 3 подтемы x {len(TYPES)} типа = {len(cells)} клеток, по {PER_CELL} примера на клетку")


# ---------- 2. Игрушечная «модель-учитель» ----------
def mock_teacher(topic, sub, kind, n):
    """Возвращает n пар (instruction, response). Добавляет типичные дефекты генерации."""
    out = []
    for _ in range(n):
        instr = rng.choice(TYPES[kind]).format(s=sub)
        resp = f"Коротко про {sub}: это часть темы «{topic}». Главное правило: проверяйте результат на данных."
        roll = rng.random()
        if roll < 0.07:
            instr = "Что это?"                                    # слишком коротко
        elif roll < 0.12:
            instr = (instr + " Подробно опиши историю, ") * 4     # слишком длинно
        elif roll < 0.18:
            resp = instr                                          # ответ повторяет вход
        elif roll < 0.24:
            resp = f"Другой вариант ответа про {sub}: смотрите документацию."  # конфликтующий ответ позже
        out.append({"topic": topic, "sub": sub, "kind": kind, "instruction": instr, "response": resp})
    return out


def generate(cell_list, n):
    rows = []
    for t, s, k in cell_list:
        rows.extend(mock_teacher(t, s, k, n))
    return rows


# ---------- 3. Фильтры ----------
def apply_filters(rows):
    steps = []
    cur = rows
    # 1. точные повторы (instruction + response)
    seen, nxt = set(), []
    for r in cur:
        key = (r["instruction"], r["response"])
        if key not in seen:
            seen.add(key); nxt.append(r)
    steps.append(("точные повторы", len(cur) - len(nxt))); cur = nxt
    # 2. длина инструкции (в словах)
    nxt = [r for r in cur if 4 <= len(r["instruction"].split()) <= 25]
    steps.append(("инструкция слишком короткая или длинная", len(cur) - len(nxt))); cur = nxt
    # 3. ответ повторяет вход
    nxt = [r for r in cur if r["response"] != r["instruction"]]
    steps.append(("ответ повторяет инструкцию", len(cur) - len(nxt))); cur = nxt
    # 4. одна инструкция, разные ответы: убираем всю группу, пока не разберёмся
    answers = defaultdict(set)
    for r in cur:
        answers[r["instruction"]].add(r["response"])
    nxt = [r for r in cur if len(answers[r["instruction"]]) == 1]
    steps.append(("одна инструкция с разными ответами", len(cur) - len(nxt))); cur = nxt
    return cur, steps


def matrix(rows):
    c = Counter((r["topic"], r["kind"]) for r in rows)
    print(f"{'тема':<17}" + "".join(f"{k:>9}" for k in TYPES))
    for t in TOPICS:
        print(f"{t:<17}" + "".join(f"{c[(t, k)]:>9}" for k in TYPES))


raw = generate(cells, PER_CELL)
print(f"\nСгенерировано: {len(raw)} примеров")
good, steps = apply_filters(raw)
print("Воронка фильтров:")
for name, removed in steps:
    print(f"  - {name}: убрано {removed}")
print(f"Осталось: {len(good)} из {len(raw)} ({100 * len(good) / len(raw):.0f}%)")
print("\nCoverage после фильтров (число примеров на тему и тип):")
matrix(good)

# ---------- 4. Дозаполняем тонкие клетки ----------
by_cell = Counter((r["topic"], r["sub"], r["kind"]) for r in good)
thin = [c for c in cells if by_cell[c] < PER_CELL - 1]
print(f"\nТонких клеток плана (меньше {PER_CELL - 1} примеров): {len(thin)} из {len(cells)}")
extra = generate(thin, 2)
good2, _ = apply_filters(good + extra)
by_cell2 = Counter((r["topic"], r["sub"], r["kind"]) for r in good2)
thin2 = [c for c in cells if by_cell2[c] < PER_CELL - 1]
print(f"После второго прохода: {len(good2)} примеров, тонких клеток: {len(thin2)}")
