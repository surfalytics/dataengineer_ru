"""Собирает учебные файлы для курса «Базовый минимум Docker».

Результат: public/assets/practice/docker-practice.tar.gz
Запуск из корня репозитория: python3 scripts/docker-practice/build.py

Данные генерируются с фиксированным seed, поэтому архив каждый раз одинаковый.
Ответы в уроках (src/content/docs/practice/docker/) посчитаны на этих данных.
Если меняете генератор или скрипты, пересчитайте ответы в уроках.
"""

import io
import random
import tarfile
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = "docker-practice"
OUT = Path("public/assets/practice/docker-practice.tar.gz")
MTIME = int(datetime(2024, 4, 1).timestamp())

rnd = random.Random(11)
files: dict[str, str] = {}

# --- orders.csv: 500 заказов интернет-магазина ------------------------------
CHANNELS = ["organic"] * 40 + ["ads"] * 35 + ["email"] * 25
STATUSES = ["completed"] * 84 + ["cancelled"] * 10 + ["refunded"] * 6
rows = ["order_id,order_date,customer_id,channel,amount,status"]
start = date(2024, 1, 1)
for i in range(1, 501):
    d = start + timedelta(days=rnd.randint(0, 89))
    amount = round(rnd.uniform(10, 300), 2)
    rows.append(
        f"{1000 + i},{d},{rnd.randint(1, 120)},{rnd.choice(CHANNELS)},"
        f"{amount:.2f},{rnd.choice(STATUSES)}"
    )
files["data/orders.csv"] = "\n".join(rows) + "\n"

# --- app/report.py: только стандартная библиотека ---------------------------
files["app/report.py"] = '''\
"""Читает orders.csv и печатает выручку по каналам. Только стандартная библиотека."""

import csv
import os
from collections import defaultdict

path = os.environ.get("ORDERS_PATH", "/data/orders.csv")

revenue = defaultdict(float)
count = 0
with open(path, newline="") as f:
    for row in csv.DictReader(f):
        count += 1
        if row["status"] == "completed":
            revenue[row["channel"]] += float(row["amount"])

print(f"Файл: {path}")
print(f"Заказов: {count}")
print("Выручка по каналам (только completed):")
for channel, total in sorted(revenue.items(), key=lambda x: -x[1]):
    print(f"  {channel:<8} {total:>10.2f}")
'''

# --- app/load_orders.py: грузит CSV в Postgres (нужен psycopg) ---------------
files["app/load_orders.py"] = '''\
"""Загружает orders.csv в таблицу orders в Postgres."""

import csv
import os

import psycopg

path = os.environ.get("ORDERS_PATH", "/data/orders.csv")

conn = psycopg.connect(
    host=os.environ.get("DB_HOST", "localhost"),
    port=os.environ.get("DB_PORT", "5432"),
    dbname=os.environ.get("DB_NAME", "shop"),
    user=os.environ.get("DB_USER", "postgres"),
    password=os.environ["DB_PASSWORD"],
)

with conn, conn.cursor() as cur:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id    integer PRIMARY KEY,
            order_date  date,
            customer_id integer,
            channel     text,
            amount      numeric(10, 2),
            status      text
        )
    """)
    cur.execute("TRUNCATE orders")
    with open(path, newline="") as f:
        rows = [
            (r["order_id"], r["order_date"], r["customer_id"],
             r["channel"], r["amount"], r["status"])
            for r in csv.DictReader(f)
        ]
    cur.executemany("INSERT INTO orders VALUES (%s, %s, %s, %s, %s, %s)", rows)
    print(f"Загружено строк: {len(rows)}")
'''

files["app/requirements.txt"] = "psycopg[binary]==3.3.8\n"

files["README.txt"] = (
    "Учебные файлы курса «Базовый минимум Docker» с dataengineer.ru\n"
    "https://dataengineer.ru/practice/docker/\n\n"
    "data/orders.csv         500 заказов интернет-магазина\n"
    "app/report.py           печатает выручку по каналам (только стандартная библиотека)\n"
    "app/load_orders.py      грузит orders.csv в Postgres (нужен psycopg)\n"
    "app/requirements.txt    зависимости для load_orders.py\n"
)

# --- Архив -----------------------------------------------------------------
OUT.parent.mkdir(parents=True, exist_ok=True)
dirs = {ROOT, f"{ROOT}/data", f"{ROOT}/app"}
with tarfile.open(OUT, "w:gz", format=tarfile.PAX_FORMAT) as tar:
    for d in sorted(dirs):
        info = tarfile.TarInfo(d)
        info.type, info.mode, info.mtime = tarfile.DIRTYPE, 0o755, MTIME
        tar.addfile(info)
    for p in sorted(files):
        data = files[p].encode("utf-8")
        info = tarfile.TarInfo(f"{ROOT}/{p}")
        info.size, info.mode, info.mtime = len(data), 0o644, MTIME
        tar.addfile(info, io.BytesIO(data))

print(f"{OUT}: {OUT.stat().st_size // 1024} KB, {len(files)} files")
