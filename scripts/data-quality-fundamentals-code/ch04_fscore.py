"""Глава 4: precision, recall и F-score для детектора свежести.
Детектор: «пропуск длиннее T дней — это аномалия». Метки (что было настоящим инцидентом) задаём сами.
Запуск: python3 -I scripts/data-quality-fundamentals-code/ch04_fscore.py   (только стандартная библиотека)"""

# (дата, дней без обновления, настоящий ли инцидент) - те же шесть пропусков, что в практике на DuckDB
OUTAGES = [
    ("2024-02-10", 8, True),
    ("2024-03-23", 4, False),
    ("2024-05-18", 8, True),
    ("2024-06-06", 3, False),
    ("2024-06-22", 5, True),
    ("2024-07-10", 3, True),
]


def f_beta(p, r, beta):
    """F-beta = (1 + b^2) * P * R / (b^2 * P + R). beta > 1: важнее recall."""
    if p + r == 0:
        return 0.0
    return (1 + beta**2) * p * r / (beta**2 * p + r)


def score(threshold):
    tp = sum(1 for _, gap, real in OUTAGES if gap > threshold and real)
    fp = sum(1 for _, gap, real in OUTAGES if gap > threshold and not real)
    fn = sum(1 for _, gap, real in OUTAGES if gap <= threshold and real)
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    return tp, fp, fn, p, r


print("порог T | TP FP FN | precision recall |   F1   F2  F0.5")
for t in range(1, 8):
    tp, fp, fn, p, r = score(t)
    print(f"{t:>7} | {tp:>2} {fp:>2} {fn:>2} | {p:>9.2f} {r:>6.2f} | "
          f"{f_beta(p, r, 1):.3f} {f_beta(p, r, 2):.3f} {f_beta(p, r, 0.5):.3f}")

best = max(range(1, 8), key=lambda t: (round(f_beta(*score(t)[3:], 1), 6), -t))
print("лучший порог по F1:", best)

# Ловушка accuracy: детектор «никогда не тревожусь» на 1000 проверках, из них 4 настоящих инцидента
checks, incidents = 1000, 4
accuracy = (checks - incidents) / checks
print(f"\nдетектор «всегда ОК»: accuracy = {accuracy:.1%}, recall = 0.0, precision не определена")
