"""Глава 3: circuit breaker для пайплайна. Проверки свежести, объёма и схемы.
Если критичная проверка не прошла, цепь открыта и следующие шаги не запускаются.
Запуск: python3 scripts/data-quality-fundamentals-code/ch03_circuit_breaker.py   (только стандартная библиотека)"""
from datetime import datetime, timedelta

NOW = datetime(2024, 3, 10, 12, 0)
EXPECTED_COLUMNS = ["order_id", "customer_id", "amount", "created_at"]


def check_freshness(batch):
    age = NOW - batch["loaded_at"]
    return age <= timedelta(hours=6), f"возраст данных {age}, максимум 6:00:00"


def check_volume(batch):
    n = len(batch["rows"])
    return 800 <= n <= 1200, f"строк {n}, ожидаем от 800 до 1200"


def check_schema(batch):
    missing = [c for c in EXPECTED_COLUMNS if c not in batch["columns"]]
    return not missing, f"нет колонок: {missing}" if missing else "все колонки на месте"


def check_nulls(batch):
    share = batch["null_customers"] / len(batch["rows"])
    return share <= 0.01, f"доля пустых customer_id {share:.1%}, максимум 1.0%"


# (название, функция, критичная ли проверка)
CHECKS = [("freshness", check_freshness, True),
          ("volume", check_volume, True),
          ("schema", check_schema, True),
          ("nulls", check_nulls, False)]


def run_pipeline(batch):
    circuit_open = False
    for name, fn, critical in CHECKS:
        ok, msg = fn(batch)
        status = "OK  " if ok else ("STOP" if critical else "WARN")
        print(f"  [{status}] {name}: {msg}")
        if not ok and critical:
            circuit_open = True
    if circuit_open:
        print("  цепь ОТКРЫТА: transform и load не запущены, алерт отправлен владельцу")
    else:
        print("  цепь ЗАКРЫТА: transform и load запущены")


good = {"loaded_at": datetime(2024, 3, 10, 9, 0), "rows": range(1000), "columns": EXPECTED_COLUMNS, "null_customers": 2}
bad = {"loaded_at": datetime(2024, 3, 9, 20, 0), "rows": range(120), "columns": ["order_id", "amount", "created_at"], "null_customers": 0}
warn = {"loaded_at": datetime(2024, 3, 10, 9, 0), "rows": range(1000), "columns": EXPECTED_COLUMNS, "null_customers": 40}

for title, batch in [("Хороший батч", good), ("Плохой батч", bad), ("Батч с мелкой проблемой", warn)]:
    print(title)
    run_pipeline(batch)
