"""Глава 3: type coercion и время в UTC на маленьких примерах.
Запуск: python3 scripts/data-quality-fundamentals-code/ch03_coercion.py   (только стандартная библиотека)"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal

print("== 1. Type coercion: float -> int")
for x in (4.00, 4.49, 4.99, -4.99):
    print(f"int({x}) = {int(x)}   round({x}) = {round(x)}")
print("int('4') =", int("4"), "  но int('4.99') даёт ошибку:", end=" ")
try:
    int("4.99")
except ValueError as e:
    print("ValueError")

print("\n== 2. Деньги: float и Decimal")
print("0.1 + 0.2 =", 0.1 + 0.2)
print("Decimal('0.1') + Decimal('0.2') =", Decimal("0.1") + Decimal("0.2"))

print("\n== 3. Локальное время в UTC")
local = [  # (локальное время события, смещение от UTC в часах)
    ("2024-03-10 09:30:00", +3),   # Москва
    ("2024-03-10 08:15:00", -5),   # Нью-Йорк
    ("2024-03-10 14:00:00", +9),   # Токио
]
for text, off in local:
    t = datetime.fromisoformat(text).replace(tzinfo=timezone(timedelta(hours=off)))
    print(f"{text} (UTC{off:+d}) -> {t.astimezone(timezone.utc).isoformat()}")
