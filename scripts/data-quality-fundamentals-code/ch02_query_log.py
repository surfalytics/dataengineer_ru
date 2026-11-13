"""Глава 2: что можно узнать из журнала запросов (query log): lineage, кто читает таблицу, когда читали в последний раз.
Запуск: python3 scripts/data-quality-fundamentals-code/ch02_query_log.py   (только стандартная библиотека)
Журнал выдуманный. Разбор SQL через регулярные выражения: это учебная замена настоящему SQL-парсеру."""
import re

# (время, пользователь, SQL): так выглядят записи в query_history
LOG = [
    ("2026-03-01 08:00", "airflow", "INSERT INTO mart.orders_daily SELECT order_date, sum(amount) FROM raw.orders GROUP BY 1"),
    ("2026-03-01 08:05", "airflow", "INSERT INTO mart.revenue SELECT d.month, sum(o.amount) FROM mart.orders_daily o JOIN dim.dates d ON o.order_date = d.d GROUP BY 1"),
    ("2026-03-01 09:10", "anna", "SELECT * FROM mart.revenue WHERE month = '2026-02'"),
    ("2026-03-01 09:40", "looker", "SELECT month, revenue FROM mart.revenue"),
    ("2026-03-02 08:00", "airflow", "INSERT INTO mart.orders_daily SELECT order_date, sum(amount) FROM raw.orders GROUP BY 1"),
    ("2026-03-02 11:30", "looker", "SELECT order_date, amount FROM mart.orders_daily"),
    ("2026-03-02 15:20", "tmp_bot", "SELECT email, phone FROM raw.customers_pii"),
    ("2026-03-03 10:00", "boris", "SELECT * FROM raw.orders WHERE order_date = '2026-03-02'"),
]
ALLOWED = {"raw.customers_pii": {"airflow"}}  # у остальных таблиц доступ открыт

WRITE = re.compile(r"INSERT\s+INTO\s+([\w.]+)", re.I)
READ = re.compile(r"(?:FROM|JOIN)\s+([\w.]+)", re.I)

edges, readers, last_read = set(), {}, {}
for ts, user, sql in LOG:
    m = WRITE.search(sql)
    target = m.group(1) if m else None
    for src in READ.findall(sql):
        if target:
            edges.add((src, target))
        else:  # запрос ничего не пишет: это чтение
            readers.setdefault(src, set()).add(user)
            last_read[src] = max(last_read.get(src, ts), ts)

print("== lineage: из чего построена таблица")
for src, dst in sorted(edges):
    print(f"{src} -> {dst}")

print("\n== кто читает таблицы и когда читали в последний раз")
for t in sorted(readers):
    print(f"{t:20} последнее чтение {last_read[t]}  читают: {', '.join(sorted(readers[t]))}")

print("\n== доступ, которого быть не должно")
for t, ok in sorted(ALLOWED.items()):
    for u in sorted(readers.get(t, set()) - ok):
        print(f"{u} читает {t}")
