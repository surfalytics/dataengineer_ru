"""Собирает учебные файлы для курса «Базовый минимум CLI».

Результат: public/assets/practice/cli-practice.tar.gz
Запуск из корня репозитория: python3 scripts/cli-practice/build.py

Данные генерируются с фиксированным seed, поэтому архив каждый раз одинаковый.
Ответы в уроках (src/content/docs/practice/cli/) посчитаны на этих данных.
Если меняете генератор, пересчитайте ответы в уроках.
"""

import io
import random
import tarfile
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = "cli-practice"
OUT = Path("public/assets/practice/cli-practice.tar.gz")
MTIME = int(datetime(2024, 4, 1).timestamp())

rnd = random.Random(42)
files: dict[str, tuple[str, int]] = {}  # путь -> (текст, права)
dirs: list[str] = []


def add(path: str, text: str, mode: int = 0o644) -> None:
    files[f"{ROOT}/{path}"] = (text, mode)


# --- Справочник клиентов ---------------------------------------------------
customers = [
    (1, "Ivan Petrov", "Russia"),
    (2, "Anna Smirnova", "Russia"),
    (3, "Aidar Nurlanov", "Kazakhstan"),
    (4, "Marko Jovanovic", "Serbia"),
    (5, "Nino Beridze", "Georgia"),
    (6, "Olga Ivanova", "Russia"),
    (7, "Arman Sargsyan", "Armenia"),
    (8, "Dana Abenova", "Kazakhstan"),
    (9, "Sergey Volkov", "Russia"),
    (10, "Milica Petrovic", "Serbia"),
]
add("data/customers.csv", "customer_id,name,country\n" + "".join(f"{c},{n},{k}\n" for c, n, k in customers))

# --- Продажи по месяцам ----------------------------------------------------
STATUSES = ["completed"] * 8 + ["cancelled"] + ["refunded"]
order_id = 1000


def sales(year: int, month: int, n: int) -> str:
    global order_id
    days = sorted(rnd.randint(1, 28) for _ in range(n))
    lines = ["order_id,order_date,customer_id,amount,status"]
    for d in days:
        order_id += 1
        amount = round(rnd.uniform(10, 500), 2)
        lines.append(f"{order_id},{date(year, month, d)},{rnd.randint(1, 10)},{amount:.2f},{rnd.choice(STATUSES)}")
    return "\n".join(lines) + "\n"


add("data/sales_2024-01.csv", sales(2024, 1, 25))
add("data/sales_2024-02.csv", sales(2024, 2, 22))
add("data/sales_2024-03.csv", sales(2024, 3, 28))

# --- Большой файл событий --------------------------------------------------
EVENTS = ["page_view"] * 6 + ["click"] * 3 + ["signup", "purchase"]
start = datetime(2024, 3, 1)
ev = ["event_id,user_id,event_type,event_time"]
t = start
for i in range(1, 10001):
    t += timedelta(seconds=rnd.randint(30, 400))
    ev.append(f"{i},{rnd.randint(1, 500)},{rnd.choice(EVENTS)},{t:%Y-%m-%d %H:%M:%S}")
add("data/events.csv", "\n".join(ev) + "\n")

# --- Лог пайплайна ---------------------------------------------------------
TABLES = ["orders", "customers", "events"]


def log_month(year: int, month: int, days: int) -> str:
    out = []
    for d in range(1, days + 1):
        ts = datetime(year, month, d, 2, 0, 0)

        def line(level: str, msg: str, sec: int) -> str:
            return f"{ts + timedelta(seconds=sec):%Y-%m-%d %H:%M:%S} {level} {msg}"

        out.append(line("INFO", "run started", 0))
        sec = 5
        failed = False
        for tbl in TABLES:
            r = rnd.random()
            if r < 0.06:
                out.append(line("ERROR", f"load failed table={tbl} reason=connection timeout", sec))
                failed = True
                break
            if r < 0.15:
                out.append(line("WARN", f"slow query table={tbl} seconds={rnd.randint(60, 300)}", sec))
                sec += 3
            out.append(line("INFO", f"loaded table={tbl} rows={rnd.randint(100, 5000)}", sec))
            sec += rnd.randint(5, 40)
        out.append(line("ERROR" if failed else "INFO", "run failed" if failed else "run finished", sec))
    return "\n".join(out) + "\n"


add("logs/pipeline.log", log_month(2024, 3, 31))
add("logs/archive/pipeline_2024-01.log", log_month(2024, 1, 31))
add("logs/archive/pipeline_2024-02.log", log_month(2024, 2, 29))

# --- Конфиг и скрипт -------------------------------------------------------
add(
    "config/app.env",
    "# Настройки подключения. Пароль ненастоящий.\n"
    "DB_HOST=warehouse.example.com\nDB_PORT=5432\nDB_NAME=analytics\nDB_USER=analyst\nDB_PASSWORD=not-a-real-password\n",
)
add(
    "scripts/report.sh",
    "#!/usr/bin/env bash\n"
    "# Считает число заказов в каждом файле продаж.\n"
    'for f in data/sales_*.csv; do\n'
    '  echo "$f: $(tail -n +2 "$f" | wc -l | tr -d \' \') orders"\n'
    "done\n",
    0o644,  # специально без права на запуск: его добавляем в уроке про chmod
)

# --- «Выгрузка от поставщика» для итоговой практики ------------------------
add("inbox/sales_2024-04.csv", sales(2024, 4, 20))
add("inbox/sales_2024-05.csv", sales(2024, 5, 24))
add(
    "inbox/products.csv",
    "product_id,name,category\n1,Laptop,electronics\n2,Monitor,electronics\n3,Chair,furniture\n4,Desk,furniture\n5,Headphones,electronics\n",
)
add(
    "inbox/notes.txt",
    "Data drop from the vendor.\nSales files are monthly. products.csv is reference data.\nThe tmp files are leftovers: delete them.\n",
)
add("inbox/.env", "API_KEY=not-a-real-key\n")
for i in range(1, 4):
    add(f"inbox/tmp_export_0{i}.bak", "")
dirs.append(f"{ROOT}/inbox/old")

add(
    "README.txt",
    "Учебные файлы курса «Базовый минимум CLI» с dataengineer.ru\n"
    "https://dataengineer.ru/practice/cli/\n\n"
    "data/     продажи, клиенты, события\n"
    "logs/     логи пайплайна\n"
    "config/   настройки подключения (пароль ненастоящий)\n"
    "scripts/  скрипт отчёта\n"
    "inbox/    выгрузка от поставщика для итоговой практики\n",
)

# --- Архив -----------------------------------------------------------------
OUT.parent.mkdir(parents=True, exist_ok=True)
all_dirs = set(dirs)
for p in files:
    parts = p.split("/")[:-1]
    for i in range(1, len(parts) + 1):
        all_dirs.add("/".join(parts[:i]))

with tarfile.open(OUT, "w:gz", format=tarfile.PAX_FORMAT) as tar:
    for d in sorted(all_dirs):
        info = tarfile.TarInfo(d)
        info.type, info.mode, info.mtime = tarfile.DIRTYPE, 0o755, MTIME
        tar.addfile(info)
    for p in sorted(files):
        text, mode = files[p]
        data = text.encode("utf-8")
        info = tarfile.TarInfo(p)
        info.size, info.mode, info.mtime = len(data), mode, MTIME
        tar.addfile(info, io.BytesIO(data))

print(f"{OUT}: {OUT.stat().st_size // 1024} KB, {len(files)} files")
