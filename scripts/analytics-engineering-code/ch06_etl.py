#!/usr/bin/env python3
"""Глава 6: учебный ETL-скрипт по мотивам примеров 6-4...6-8.
В книге: MySQL -> pandas -> BigQuery (pandas_gbq).
Здесь: только стандартная библиотека. Источник и приёмник - две базы SQLite в памяти.
Логика та же: найти все таблицы по метаданным, извлечь, почистить даты, загрузить с заменой.
Запуск: python3 -I scripts/analytics-engineering-code/ch06_etl.py"""
import sqlite3
from datetime import date

sqlite3.register_adapter(date, lambda d: d.isoformat())
sqlite3.register_converter("DATE", lambda b: date.fromisoformat(b.decode()))


def make_source():
    """Операционная база (в книге - MySQL OMNI_MANAGEMENT) с тестовыми строками."""
    db = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
    db.executescript("""
        CREATE TABLE channels (channel_id INTEGER PRIMARY KEY, channel_name TEXT,
            created_at TEXT DEFAULT '2024-01-01 00:00:00', updated_at TEXT DEFAULT '2024-01-01 00:00:00');
        CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT, date_birth DATE,
            created_at TEXT DEFAULT '2024-01-01 00:00:00', updated_at TEXT DEFAULT '2024-01-01 00:00:00');
        CREATE TABLE purchase_history (customer_id INTEGER REFERENCES customers,
            channel_id INTEGER REFERENCES channels, quantity INTEGER, order_date TEXT NOT NULL);
    """)
    db.executemany("INSERT INTO channels (channel_id, channel_name) VALUES (?, ?)",
                   [(1, "Website"), (2, "Mobile App"), (3, "Instagram")])
    db.executemany("INSERT INTO customers (customer_id, name, date_birth) VALUES (?, ?, ?)",
                   [(1, "Анна", date(1990, 4, 12)), (2, "Иван", date(1985, 11, 3))])
    db.executemany("INSERT INTO purchase_history VALUES (?, ?, ?, ?)",
                   [(1, 2, 1, "2024-03-01 10:15:00"), (2, 1, 2, "2024-03-02 18:40:00")])
    return db


def extract_table(table_name, conn):
    """Extract: вся таблица целиком. В жизни лучше брать только строки с updated_at > прошлой выгрузки."""
    cur = conn.execute(f"SELECT * FROM {table_name}")
    cols = [c[0] for c in cur.description]
    return cols, cur.fetchall()


def transform_rows(cols, rows):
    """Transform: даты превращаем в строки, как в книге (там это нужно для pandas_gbq)."""
    return [tuple(str(v) if isinstance(v, date) else v for v in row) for row in rows]


def load_table(target, table_name, cols, rows):
    """Load: заменяем таблицу целиком (в книге if_exists='replace')."""
    target.execute(f"DROP TABLE IF EXISTS {table_name}")
    target.execute(f"CREATE TABLE {table_name} ({', '.join(cols)})")
    marks = ", ".join("?" * len(cols))
    target.executemany(f"INSERT INTO {table_name} VALUES ({marks})", rows)


def pipeline(source, target):
    # Список таблиц берём из метаданных (в MySQL - information_schema.tables)
    tables = [r[0] for r in source.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")]
    for table in tables:
        cols, rows = extract_table(table, source)
        rows = transform_rows(cols, rows)
        load_table(target, table, cols, rows)
        print(f"Загружена таблица {table}, строк: {len(rows)}")


if __name__ == "__main__":
    src = make_source()
    raw = sqlite3.connect(":memory:")  # приёмник: в книге датасет omnichannel_raw в BigQuery
    pipeline(src, raw)
    print(raw.execute("SELECT customer_id, name, date_birth, typeof(date_birth) FROM customers").fetchall())
