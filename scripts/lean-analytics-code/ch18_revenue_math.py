#!/usr/bin/env python3
"""Глава 18: magic number для SaaS и срок окупаемости клиента (таблица 18-1).
Запуск: python3 -I scripts/lean-analytics-code/ch18_revenue_math.py  (только стандартная библиотека)"""


def magic_number(qrr_now, qrr_prev, sm_prev):
    """Прирост квартального повторяющегося дохода на доллар расходов на продажи и маркетинг."""
    return (qrr_now - qrr_prev) / sm_prev


# Две выдуманные SaaS-компании: QRR прошлого и текущего квартала, расходы прошлого квартала, $
companies = {
    "A": (400_000, 460_000, 50_000),
    "B": (400_000, 430_000, 50_000),
}
for name, (prev, now, sm) in companies.items():
    m = magic_number(now, prev, sm)
    verdict = "жмём на газ" if m > 1 else ("изъян в модели" if m < 0.75 else "серая зона")
    print(f"Компания {name}: magic number = {m:.2f} -> {verdict}")

# Таблица 18-1: клиент приносит $27 за 11 месяцев, привлечение стоит $14
ltv, months, cac = 27, 11, 14
arpu = ltv / months
payback = cac / arpu
print(f"\nДоход на клиента в месяц: ${arpu:.2f}")
print(f"Окупаемость клиента:      {payback:.1f} мес.")

# Денежный поток по одному клиенту: сначала платим CAC, потом он платит нам каждый месяц
print("\nМесяц  Накоплено, $")
for m in range(0, months + 1, 2):
    print(f"{m:>5}  {arpu * m - cac:>11.2f}")
