"""Собирает учебные файлы для курса «Базовый минимум Dimensional Modeling».

Результат: public/assets/practice/modeling-practice.tar.gz
Запуск из корня репозитория: python3 scripts/modeling-practice/build.py

Источник — OLTP-база магазина спортивных товаров «Волна» (3NF), выгруженная в CSV.
Данные генерируются с фиксированным seed, поэтому архив каждый раз одинаковый.
Ответы в уроках (src/content/docs/practice/modeling/) посчитаны на этих данных.
Если меняете генератор, пересчитайте ответы: python3 scripts/modeling-practice/check_sql.py
"""

import gzip
import io
import tarfile
from datetime import date, datetime, timedelta
from pathlib import Path
import random

ROOT = "modeling-practice"
OUT = Path("public/assets/practice/modeling-practice.tar.gz")
MTIME = int(datetime(2025, 7, 1).timestamp())
START, END = date(2025, 1, 1), date(2025, 6, 30)

rnd = random.Random(42)
files: dict[str, str] = {}


def csv(header: str, rows: list[tuple]) -> str:
    def cell(v):
        return "" if v is None else str(v)
    return header + "\n" + "\n".join(",".join(cell(v) for v in r) for r in rows) + "\n"


# --- Справочники ------------------------------------------------------------
CATEGORIES = [(1, "Одежда"), (2, "Обувь"), (3, "Электроника"), (4, "Аксессуары"), (5, "Снаряжение")]

PRODUCTS = [  # product_id, sku, name, category_id, brand, list_price
    (1, "SKU-1001", "Футболка беговая", 1, "Volna", 1990),
    (2, "SKU-1002", "Худи", 1, "Volna", 4990),
    (3, "SKU-1003", "Шорты", 1, "Stride", 2490),
    (4, "SKU-1004", "Куртка-ветровка", 1, "Stride", 7990),
    (5, "SKU-2001", "Кроссовки беговые", 2, "Stride", 8990),
    (6, "SKU-2002", "Кеды", 2, "Urban", 5490),
    (7, "SKU-2003", "Трейловые кроссовки", 2, "Stride", 11990),
    (8, "SKU-2004", "Сандалии", 2, "Urban", 2990),
    (9, "SKU-3001", "Смарт-часы", 3, "Pulse", 19990),
    (10, "SKU-3002", "Наушники беспроводные", 3, "Pulse", 9990),
    (11, "SKU-3003", "Фитнес-браслет", 3, "Pulse", 4990),
    (12, "SKU-3004", "Велокомпьютер", 3, "Pulse", 6990),
    (13, "SKU-4001", "Рюкзак", 4, "Urban", 4490),
    (14, "SKU-4002", "Бутылка для воды", 4, "Volna", 990),
    (15, "SKU-4003", "Кепка", 4, "Volna", 1490),
    (16, "SKU-4004", "Носки", 4, "Volna", 590),
    (17, "SKU-5001", "Коврик для йоги", 5, "Zen", 2990),
    (18, "SKU-5002", "Гантели 5 кг", 5, "Iron", 3490),
    (19, "SKU-5003", "Скакалка", 5, "Iron", 790),
    (20, "SKU-5004", "Велосипедный шлем", 5, "Iron", 5990),
]
# 1 апреля 2025 цены на четыре товара выросли на 10%.
PRICE_UP = {1, 5, 9, 10}
PRICE_UP_DATE = date(2025, 4, 1)


def price(pid: int, d: date) -> int:
    p = PRODUCTS[pid - 1][5]
    return round(p * 1.1 / 10) * 10 if pid in PRICE_UP and d >= PRICE_UP_DATE else p


STORES = [  # store_id, name, city, region, store_type, opened_on
    (1, "Онлайн-магазин", "Москва", "Центр", "online", "2019-03-01"),
    (2, "ТЦ Авиапарк", "Москва", "Центр", "offline", "2020-09-15"),
    (3, "Невский", "Санкт-Петербург", "Северо-Запад", "offline", "2021-04-10"),
    (4, "Казань Молл", "Казань", "Поволжье", "offline", "2022-06-01"),
]
STORE_W = [45, 25, 18, 12]
NOT_IN_STORE = {(4, 12)}  # Казань не продаёт велокомпьютеры

files["data/categories.csv"] = csv("category_id,category_name", CATEGORIES)
files["data/products.csv"] = csv(
    "product_id,sku,product_name,category_id,brand,list_price",
    [p[:5] + (price(p[0], END),) for p in PRODUCTS],
)
files["data/stores.csv"] = csv("store_id,store_name,city,region,store_type,opened_on", STORES)

# --- Клиенты: состояние на 1 января 2025 -----------------------------------
MALE_F = ["Иван", "Алексей", "Дмитрий", "Сергей", "Андрей", "Максим", "Павел", "Егор", "Никита", "Артём"]
FEMALE_F = ["Анна", "Мария", "Елена", "Ольга", "Наталья", "Дарья", "Ксения", "Полина", "Софья", "Ирина"]
LAST = ["Иванов", "Смирнов", "Кузнецов", "Попов", "Волков", "Соколов", "Лебедев", "Козлов", "Новиков", "Морозов",
        "Орлов", "Фёдоров", "Михайлов", "Белов", "Тарасов", "Захаров", "Зайцев", "Павлов", "Семёнов", "Голубев"]
CITIES = ["Москва"] * 40 + ["Санкт-Петербург"] * 25 + ["Казань"] * 15 + ["Екатеринбург"] * 12 + ["Новосибирск"] * 8

customers = {}
for cid in range(1, 301):
    male = rnd.random() < 0.5
    first = rnd.choice(MALE_F if male else FEMALE_F)
    last = rnd.choice(LAST) + ("" if male else "а")
    signup = date(2023, 1, 1) + timedelta(days=rnd.randint(0, 729))
    customers[cid] = {
        "name": f"{first} {last}",
        "email": f"user{cid}@example.com",
        "city": rnd.choice(CITIES),
        "segment": "VIP" if rnd.random() < 0.15 else "Обычный",
        "signup": signup,
    }
files["data/customers.csv"] = csv(
    "customer_id,customer_name,email,city,segment,signup_date",
    [(c, v["name"], v["email"], v["city"], v["segment"], v["signup"]) for c, v in customers.items()],
)

# --- Журнал изменений клиентов (CDC) за полгода -----------------------------
# Переезды и переход в VIP. Нужны для урока про SCD.
changes = []
state = {c: (v["city"], v["segment"]) for c, v in customers.items()}
movers = rnd.sample(range(1, 301), 25)
for i, cid in enumerate(movers):
    n = 2 if i < 5 else 1  # пять клиентов меняются дважды
    days = sorted(rnd.sample(range(31, 150), n))
    for d in days:
        city, seg = state[cid]
        if seg == "Обычный" and rnd.random() < 0.3:
            seg = "VIP"
        else:
            city = rnd.choice([x for x in sorted(set(CITIES)) if x != city])
        state[cid] = (city, seg)
        changes.append((START + timedelta(days=d), cid, city, seg))
changes.sort()
files["data/customer_changes.csv"] = csv(
    "change_id,customer_id,changed_at,city,segment",
    [(i + 1, c, d, city, seg) for i, (d, c, city, seg) in enumerate(changes)],
)


def city_at(cid: int, d: date) -> str:
    city = customers[cid]["city"]
    for cd, c, ccity, _ in changes:
        if c == cid and cd <= d:
            city = ccity
    return city


# --- Заказы и позиции ------------------------------------------------------
orders, items = [], []
days = [START + timedelta(days=k) for k in range((END - START).days + 1)]
day_w = [(1 + 0.06 * d.month) * (1.4 if d.weekday() >= 5 else 1.0) for d in days]
oid = 10000
for _ in range(2000):
    oid += 1
    d = rnd.choices(days, day_w)[0]
    store = rnd.choices([1, 2, 3, 4], STORE_W)[0]
    store_city = STORES[store - 1][2]
    if store != 1 and rnd.random() < 0.15:
        cid = None  # покупка без карты лояльности
    else:
        local = [c for c in customers if city_at(c, d) == store_city]
        cid = rnd.choice(local) if store != 1 and rnd.random() < 0.8 else rnd.randint(1, 300)
    n_lines = rnd.choices([1, 2, 3, 4], [50, 30, 15, 5])[0]
    allowed = [p[0] for p in PRODUCTS if (store, p[0]) not in NOT_IN_STORE]
    total = 0
    for ln, pid in enumerate(rnd.sample(allowed, n_lines), start=1):
        qty = rnd.choices([1, 2, 3], [70, 22, 8] if pid not in (14, 16, 19) else [40, 35, 25])[0]
        up = price(pid, d)
        disc = round(up * qty * 0.1) if rnd.random() < 0.15 else 0
        total += up * qty - disc
        items.append((oid, ln, pid, qty, up, disc))
    if store == 1:
        ship = 0 if total >= 5000 else 399
        shipped = d + timedelta(days=rnd.choices([0, 1, 2], [30, 50, 20])[0])
        delivered = shipped + timedelta(days=rnd.randint(1, 4))
        if rnd.random() < 0.04:
            status, shipped, delivered = "cancelled", None, None
        elif shipped > END:
            status, shipped, delivered = "new", None, None
        elif delivered > END:
            status, delivered = "shipped", None
        else:
            status = "delivered"
    else:
        ship, shipped, delivered, status = 0, d, d, "delivered"
    orders.append((oid, cid, store, d, status, shipped, delivered, ship))

files["data/orders.csv"] = csv(
    "order_id,customer_id,store_id,order_date,status,shipped_date,delivered_date,shipping_cost", orders
)
files["data/order_items.csv"] = csv(
    "order_id,line_number,product_id,quantity,unit_price,discount_amount", items
)

# --- Остатки на складах: снимок на конец каждого дня июня -------------------
order_by_id = {o[0]: o for o in orders}
sold = {}
for o_id, ln, pid, qty, up, disc in items:
    o = order_by_id[o_id]
    if o[4] != "cancelled":
        k = (o[3], o[2], pid)
        sold[k] = sold.get(k, 0) + qty
inv = []
for store in (1, 2, 3, 4):
    for p in PRODUCTS:
        pid = p[0]
        if (store, pid) in NOT_IN_STORE:
            continue
        cap = rnd.randint(40, 80) if store == 1 else rnd.randint(8, 25)
        stock = cap
        for d in days:
            stock = max(0, stock - sold.get((d, store, pid), 0))
            if d.weekday() == 0 and stock < cap // 3:
                stock = cap  # поставка по понедельникам
            if d.month == 6:
                inv.append((d, store, pid, stock))
files["data/inventory.csv"] = csv("snapshot_date,store_id,product_id,quantity_on_hand", inv)

# --- Возвраты (для итоговой практики) ---------------------------------------
REASONS = ["Не подошёл размер", "Брак", "Передумал", "Не совпадает с описанием"]
rets = []
for o_id, ln, pid, qty, up, disc in items:
    o = order_by_id[o_id]
    if o[4] != "delivered":
        continue
    cat = PRODUCTS[pid - 1][3]
    p_ret = {1: 0.08, 2: 0.12}.get(cat, 0.04)
    if rnd.random() < p_ret:
        rd = o[6] + timedelta(days=rnd.randint(1, 14))
        if rd > END:
            continue
        reason = rnd.choices(REASONS, [50, 20, 20, 10] if cat in (1, 2) else [5, 45, 30, 20])[0]
        rets.append((rd, o_id, ln, rnd.randint(1, qty), reason))
rets.sort()
files["data/returns.csv"] = csv(
    "return_id,order_id,line_number,return_date,quantity,reason",
    [(i + 1, o, ln, d, q, r) for i, (d, o, ln, q, r) in enumerate(rets)],
)

files["README.txt"] = (
    "Учебные файлы курса «Базовый минимум Dimensional Modeling» с dataengineer.ru\n"
    "https://dataengineer.ru/practice/modeling/\n\n"
    "Выгрузка из OLTP-базы магазина спортивных товаров «Волна». Январь–июнь 2025.\n\n"
    "data/categories.csv        категории товаров\n"
    "data/products.csv          товары (текущая цена)\n"
    "data/stores.csv            магазины\n"
    "data/customers.csv         клиенты на 1 января 2025\n"
    "data/customer_changes.csv  журнал изменений клиентов (переезды, VIP)\n"
    "data/orders.csv            заказы (шапка)\n"
    "data/order_items.csv       позиции заказов\n"
    "data/inventory.csv         остатки на конец дня, июнь 2025\n"
    "data/returns.csv           возвраты\n"
)

# --- Архив -----------------------------------------------------------------
OUT.parent.mkdir(parents=True, exist_ok=True)
dirs = {ROOT, f"{ROOT}/data"}
# mtime=0 в gzip: архив побайтно одинаковый при каждом запуске.
with gzip.GzipFile(OUT, "wb", mtime=0) as gz, tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tar:
    for d in sorted(dirs):
        info = tarfile.TarInfo(d)
        info.type, info.mode, info.mtime = tarfile.DIRTYPE, 0o755, MTIME
        tar.addfile(info)
    for p in sorted(files):
        data = files[p].encode("utf-8")
        info = tarfile.TarInfo(f"{ROOT}/{p}")
        info.size, info.mode, info.mtime = len(data), 0o644, MTIME
        tar.addfile(info, io.BytesIO(data))

for p in sorted(files):
    print(f"{p}: {files[p].count(chr(10)) - 1} rows")
print(f"{OUT}: {OUT.stat().st_size // 1024} KB, {len(files)} files")
