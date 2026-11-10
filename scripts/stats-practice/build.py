"""Собирает учебные файлы для курса «Базовый минимум статистики».

Результат: public/assets/practice/stats-practice.tar.gz
Запуск из корня репозитория: python3 scripts/stats-practice/build.py

Данные генерируются с фиксированным seed, поэтому архив каждый раз одинаковый.
Ответы в уроках (src/content/docs/practice/stats/) посчитаны на этих данных.
Если меняете генератор, пересчитайте ответы в уроках.
"""

import io
import math
import random
import tarfile
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = "stats-practice"
OUT = Path("public/assets/practice/stats-practice.tar.gz")
MTIME = int(datetime(2024, 4, 1).timestamp())

rnd = random.Random(7)
files: dict[str, str] = {}

# --- orders.csv: 1000 заказов интернет-магазина ----------------------------
# amount: перекошенное распределение (много маленьких, мало больших) + 5 выбросов.
# delivery_hours: почти нормальное распределение, среднее 48 ч.
CHANNELS = ["organic"] * 40 + ["ads"] * 35 + ["email"] * 25
rows = ["order_id,order_date,customer_id,channel,device,items,amount,delivery_hours"]
start = date(2024, 1, 1)
outliers = {137, 402, 555, 801, 960}
for i in range(1, 1001):
    d = start + timedelta(days=rnd.randint(0, 89))
    items = min(6, 1 + int(rnd.expovariate(0.9)))
    amount = round(math.exp(rnd.gauss(3.7, 0.55)) * (0.6 + 0.4 * items), 2)
    if i in outliers:
        amount = round(rnd.uniform(2500, 4500), 2)
    hours = round(rnd.gauss(48, 8), 1)
    rows.append(
        f"{1000 + i},{d},{rnd.randint(1, 300)},{rnd.choice(CHANNELS)},"
        f"{rnd.choice(['mobile', 'desktop'])},{items},{amount:.2f},{hours}"
    )
files["data/orders.csv"] = "\n".join(rows) + "\n"

# --- daily.csv: 120 дней маркетинга ----------------------------------------
# ad_spend и visits связаны сильно, ad_spend и revenue — тоже,
# support_tickets не связаны ни с чем (для примера «нет корреляции»).
rows = ["date,ad_spend,visits,orders,revenue,support_tickets"]
for k in range(120):
    d = date(2024, 1, 1) + timedelta(days=k)
    spend = round(rnd.uniform(200, 1000), 2)
    visits = int(spend * 4.5 + rnd.gauss(0, 250) + 300)
    orders = max(1, int(visits * 0.03 + rnd.gauss(0, 4)))
    revenue = round(orders * rnd.uniform(45, 75), 2)
    tickets = rnd.randint(0, 20)
    rows.append(f"{d},{spend:.2f},{visits},{orders},{revenue:.2f},{tickets}")
files["data/daily.csv"] = "\n".join(rows) + "\n"

# --- ab_test.csv: новая кнопка «Купить» ------------------------------------
# A — старая кнопка: 200 покупок из 2000 (10%). B — новая: 250 из 2000 (12,5%).
rows = ["user_id,grp,converted"]
uid = 1
for grp, buyers in (("A", 200), ("B", 250)):
    flags = [1] * buyers + [0] * (2000 - buyers)
    rnd.shuffle(flags)
    for f in flags:
        rows.append(f"{uid},{grp},{f}")
        uid += 1
files["data/ab_test.csv"] = "\n".join(rows) + "\n"

files["README.txt"] = (
    "Учебные файлы курса «Базовый минимум статистики» с dataengineer.ru\n"
    "https://dataengineer.ru/practice/stats/\n\n"
    "data/orders.csv    1000 заказов: сумма, товары, время доставки\n"
    "data/daily.csv     120 дней маркетинга: затраты, визиты, заказы, выручка\n"
    "data/ab_test.csv   A/B-тест кнопки: 2000 пользователей в каждой группе\n"
)

# --- Архив -----------------------------------------------------------------
OUT.parent.mkdir(parents=True, exist_ok=True)
dirs = {ROOT, f"{ROOT}/data"}
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
