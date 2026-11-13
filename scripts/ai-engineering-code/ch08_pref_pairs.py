#!/usr/bin/env python3
"""Глава 8: preference data от AI-судьи и защита от position bias. Без внешних библиотек.

Что показывает скрипт:
  1. У каждой пары ответов есть скрытое «настоящее» качество, поэтому мы знаем правильного победителя.
  2. Игрушечный судья шумит и любит первую позицию (position bias).
  3. Метод NVIDIA из главы: спрашиваем судью дважды, меняя порядок ответов. Берём пару в датасет,
     только если победитель одинаковый в обоих порядках.
  4. Считаем, как меняются точность и объём.
В реальном проекте mock_judge заменяется вызовом LLM с промптом «какой ответ лучше».
Запуск из корня репозитория: python3 -I scripts/ai-engineering-code/ch08_pref_pairs.py
"""
import random

rng = random.Random(11)
N = 2000
NOISE, BIAS = 0.25, 0.15

pairs = [(rng.random(), rng.random()) for _ in range(N)]     # скрытое качество ответов A и B


def mock_judge(q_first, q_second):
    """Возвращает 0, если победил ответ на первой позиции, иначе 1."""
    score = (q_first - q_second) + rng.gauss(0, NOISE) + BIAS    # BIAS тянет к первой позиции
    return 0 if score > 0 else 1


single_correct = first_wins = 0
kept = kept_correct = 0
gaps_all, gaps_kept = [], []
for qa, qb in pairs:
    truth = "A" if qa > qb else "B"
    # один запрос: A на первой позиции
    r1 = mock_judge(qa, qb)
    w1 = "A" if r1 == 0 else "B"
    single_correct += w1 == truth
    first_wins += r1 == 0
    # второй запрос: порядок поменяли, B на первой позиции
    r2 = mock_judge(qb, qa)
    w2 = "B" if r2 == 0 else "A"
    gaps_all.append(abs(qa - qb))
    if w1 == w2:                       # судья согласен сам с собой при обоих порядках
        kept += 1
        kept_correct += w1 == truth
        gaps_kept.append(abs(qa - qb))

print(f"Пар для разметки: {N}")
print(f"Судья задан в одном порядке: победитель правильный в {100 * single_correct / N:.1f}% пар")
print(f"  первая позиция выигрывает в {100 * first_wins / N:.1f}% случаев (честно было бы 50%)")
print(f"Судья задан в двух порядках, берём только согласованные:")
print(f"  оставлено {kept} из {N} ({100 * kept / N:.1f}%)")
print(f"  победитель правильный в {100 * kept_correct / kept:.1f}% оставленных пар")
print(f"Средняя разница качества: все пары {sum(gaps_all) / len(gaps_all):.3f}, оставленные {sum(gaps_kept) / len(gaps_kept):.3f}")
print("Вывод: мы теряем спорные пары, но оставшиеся метки надёжнее. Это цена за чистый preference dataset.")
