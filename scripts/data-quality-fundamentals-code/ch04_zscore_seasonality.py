"""Глава 4: почему простой z-score плохо ловит поломки в бизнес-данных.
В воскресенье магазин закрыт, поэтому в таблице 0 строк. Это норма. В среду нулевая загрузка - это поломка.
Сравниваем z-score по всем дням и детектор, который учитывает день недели (seasonality).
Запуск: python3 -I scripts/data-quality-fundamentals-code/ch04_zscore_seasonality.py   (только стандартная библиотека)"""
import random
import statistics
from datetime import date, timedelta

random.seed(7)
START = date(2024, 1, 1)  # понедельник
WEEKS = 8
BROKEN = date(2024, 2, 14)  # среда: загрузка не пришла

days, rows = [], []
for i in range(WEEKS * 7):
    d = START + timedelta(days=i)
    n = 0 if d.weekday() == 6 else random.randint(95, 105)  # воскресенье = 0
    if d == BROKEN:
        n = 0
    days.append(d)
    rows.append(n)

# 1. z-score по всем дням: (значение - среднее) / стандартное отклонение
mu, sigma = statistics.mean(rows), statistics.pstdev(rows)
z = [(n - mu) / sigma for n in rows]
print(f"среднее = {mu:.1f}, sigma = {sigma:.1f}, z у нуля = {(0 - mu) / sigma:.2f}")


def verdict(flagged):
    sundays = sum(1 for i in flagged if days[i].weekday() == 6)
    real = BROKEN in [days[i] for i in flagged]
    return f"тревог: {len(flagged)}, из них ложных (воскресенья): {sundays}, поломка поймана: {'да' if real else 'нет'}"


print("z-score, порог 3: ", verdict([i for i, v in enumerate(z) if abs(v) > 3]))
print("z-score, порог 2: ", verdict([i for i, v in enumerate(z) if abs(v) > 2]))

# 2. Детектор с сезонностью: сравниваем с медианой того же дня недели за прошлые недели
flagged = []
for i in range(7, len(rows)):  # нужна хотя бы одна прошлая неделя
    same_weekday = [rows[j] for j in range(i % 7, i, 7)]
    base = statistics.median(same_weekday)
    if abs(rows[i] - base) > 0.3 * max(base, 1):
        flagged.append(i)
print("с учётом дня недели:", verdict(flagged))
