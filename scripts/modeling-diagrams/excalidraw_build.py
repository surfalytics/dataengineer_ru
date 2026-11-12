#!/usr/bin/env python3
"""Build the non-ER diagrams of the Dimensional Modeling course in Excalidraw (needs the canvas server on :3456).
Each diagram is a small spec (nodes at x/y, edges). Output: public/assets/practice/modeling/<name>.png
Scenes are saved as dataengineer_ru/dm-<name> in ~/dev/excalidraw/diagrams.
Usage: excalidraw_build.py [name ...]   (no args = all)"""
import base64, json, subprocess, sys, urllib.error, urllib.request
from pathlib import Path

API = "http://127.0.0.1:3456"
OUT = Path(__file__).resolve().parents[2] / "public/assets/practice/modeling"
STYLE = {  # fill, stroke
    "p": ("#a5d8ff", "#1971c2"), "g": ("#b2f2bb", "#2f9e44"), "r": ("#ffc9c9", "#e03131"),
    "y": ("#ffec99", "#f08c00"), "db": ("#99e9f2", "#0c8599"), "q": ("#ffd8a8", "#e8590c"),
    "n": ("#e9ecef", "#868e96"), "pu": ("#eebefa", "#9c36b5"),
}
W, H, FONT = 250, 100, 20

def call(path, payload=None, method="POST"):
    req = urllib.request.Request(API + path, data=json.dumps(payload or {}).encode(),
                                 headers={"content-type": "application/json"}, method=method)
    return json.load(urllib.request.urlopen(req, timeout=60))

def N(id, text, x, y, k="p", w=W, h=H, shape="rectangle"):
    return dict(id=id, text=text, x=x, y=y, k=k, w=w, h=h, shape=shape)

def E(a, b, label="", dashed=False, head=True):
    return dict(a=a, b=b, label=label, dashed=dashed, head=head)

def Z(text, x, y, w, h):  # zone rectangle + title
    return dict(zone=True, text=text, x=x, y=y, w=w, h=h)

def T(text, x, y, size=18, color="#868e96"):  # free text note
    return dict(note=True, text=text, x=x, y=y, size=size, color=color)

def build(spec):
    els = []
    for it in spec["items"]:
        if it.get("zone"):
            els.append(dict(type="rectangle", x=it["x"], y=it["y"], width=it["w"], height=it["h"],
                            backgroundColor="#f8f9fa", strokeColor="#adb5bd", fillStyle="solid",
                            strokeStyle="dashed", roughness=1, opacity=60))
            els.append(dict(type="text", x=it["x"] + 20, y=it["y"] + 12, text=it["text"], fontSize=20,
                            strokeColor="#495057", fontFamily=6))
        elif it.get("note"):
            els.append(dict(type="text", x=it["x"], y=it["y"], text=it["text"], fontSize=it["size"],
                            strokeColor=it["color"], fontFamily=6))
        else:
            f, s = STYLE[it["k"]]
            els.append(dict(id=it["id"], type=it["shape"], x=it["x"], y=it["y"], width=it["w"], height=it["h"],
                            label={"text": it["text"]}, backgroundColor=f, strokeColor=s, fillStyle="solid",
                            fontSize=FONT, fontFamily=6, strokeWidth=2, roughness=1))
    for e in spec["edges"]:
        d = dict(type="arrow", x=0, y=0, start={"id": e["a"]}, end={"id": e["b"]}, strokeWidth=2,
                 strokeColor="#495057", roughness=1,
                 endArrowhead="arrow" if e["head"] else None)
        if e["dashed"]: d["strokeStyle"] = "dashed"
        if e["label"]: d["label"] = {"text": e["label"]}
        els.append(d)
    return els

def run(name, spec):
    scene = f"dataengineer_ru/dm-{name}"
    try:
        call("/api/scenes", {"name": scene})
    except urllib.error.HTTPError as e:  # scene exists (re-run): reopen and clear it
        if e.code != 409: raise
        call("/api/scenes/open", {"name": scene})
        call("/api/elements/clear", method="DELETE")
    call("/api/elements/batch", {"elements": build(spec)})
    r = call("/api/export/image", {"format": "png", "scale": 2, "padding": 30})
    raw = OUT / f"{name}.png"
    raw.write_bytes(base64.b64decode(r["data"]))
    call("/api/scenes/save")
    subprocess.run(["node", "-e",
        "const s=require('sharp'),fs=require('fs');const p=process.argv[1];"
        "s(p).resize({width:1600,withoutEnlargement:true}).png({palette:true,quality:90,compressionLevel:9})"
        ".toBuffer().then(b=>fs.writeFileSync(p,b))", str(raw)], check=True,
        cwd=Path(__file__).resolve().parents[2])
    print("ok", name, raw.stat().st_size)

def col(i): return i * 300
def row(j): return j * 150
D = {}

# ---- why-model: шкала нормализации
D["normalization-spectrum"] = dict(items=[
    N("a", "3NF (нормализация)\nмного маленьких таблиц\nкаждый факт хранится один раз\nмного JOIN при чтении", 0, 0, "n", 440, 160),
    N("b", "Star schema (Кимбалл)\nfact table + dimension tables\ndimensions денормализованы\nодин JOIN от факта до атрибута", 0, 290, "p", 440, 160),
    N("c", "One Big Table (OBT)\nодна широкая таблица\nJOIN не нужен\nмного повторов", 0, 580, "g", 440, 160),
    T("Быстро писать.\nДля OLTP-приложений.", 500, 50),
    T("Баланс: быстро читать,\nпонятно бизнесу.", 500, 340),
    T("Проще всего читать.\nДля BI и ML.", 500, 630),
], edges=[E("a", "b", "денормализуем dimensions"), E("b", "c", "соединяем всё в одну таблицу")])

# ---- facts-dimensions: star vs snowflake
D["star-vs-snowflake"] = dict(items=[
    Z("Star: одна таблица на измерение", -20, -70, 340, 560),
    Z("Snowflake: измерение разбито", 380, -70, 340, 560),
    N("f1", "fact_sales", 20, 0, "db", 260, 80),
    N("p1", "dim_product\nproduct_name, brand,\ncategory_name", 20, 170, "p", 260, 120),
    N("f2", "fact_sales", 420, 0, "db", 260, 80),
    N("p2", "dim_product\nproduct_name, brand,\ncategory_id", 420, 170, "p", 260, 120),
    N("c2", "dim_category\ncategory_name", 420, 360, "p", 260, 90),
], edges=[E("f1", "p1"), E("f2", "p2"), E("p2", "c2", "ещё один JOIN")])

# ---- four-steps
D["four-steps"] = dict(items=[
    N("s1", "1. Бизнес-процесс\nКакое событие измеряем?\nКлиент покупает товары", 0, 0, "p", 420, 130),
    N("s2", "2. Grain\nЧто значит одна строка факта?\nОдна позиция в заказе", 0, 200, "y", 420, 130),
    N("s3", "3. Dimensions\nКто? Что? Когда? Где?\nДата, клиент, товар, магазин", 0, 400, "p", 420, 130),
    N("s4", "4. Facts\nЧто считаем числами?\nКоличество, сумма, скидка", 0, 600, "g", 420, 130),
    T("Главное решение.\nОт него зависят\nшаги 3 и 4.", 470, 225, 18, "#f08c00"),
], edges=[E("s1", "s2"), E("s2", "s3"), E("s3", "s4")])

# ---- four-steps: шапка и позиции
D["grain-header-line"] = dict(items=[
    N("o", "Онлайн-заказ (шапка, header)\norder_date, customer_id, store_id\nshipping_cost = 399", 170, 0, "p", 440, 130),
    N("l1", "Позиция 1\nКроссовки × 1\n8990", 0, 230, "db", 240, 110),
    N("l2", "Позиция 2\nНоски × 3\n1770", 270, 230, "db", 240, 110),
    N("l3", "Позиция 3\nКепка × 1\n1490", 540, 230, "db", 240, 110),
    N("w", "JOIN шапки и позиций:\nshipping_cost повторится 3 раза.\nsum(shipping_cost) = 1197, а не 399", 150, 440, "r", 480, 130),
], edges=[E("o", "l1"), E("o", "l2"), E("o", "l3"), E("l2", "w", dashed=True)])

# ---- fact-types
D["fact-types"] = dict(items=[
    Z("Transaction: одна строка на событие", -20, -70, 900, 230),
    N("t1", "10:05\nпокупка", 0, 20, "db", 250, 100), N("t2", "10:40\nпокупка", 300, 20, "db", 250, 100),
    N("t3", "12:15\nпокупка", 600, 20, "db", 250, 100),
    Z("Periodic snapshot: одна строка на период", -20, 210, 900, 230),
    N("p1", "1 июня\nостаток 27", 0, 300, "p", 250, 100), N("p2", "2 июня\nостаток 26", 300, 300, "p", 250, 100),
    N("p3", "3 июня\nостаток 26", 600, 300, "p", 250, 100),
    Z("Accumulating snapshot: одна строка на процесс", -20, 490, 900, 230),
    N("a1", "заказ создан", 0, 580, "g", 250, 100), N("a2", "отгружен", 300, 580, "g", 250, 100),
    N("a3", "доставлен", 600, 580, "g", 250, 100),
], edges=[E("a1", "a2"), E("a2", "a3")])

# ---- fact-types: accumulating snapshot заказа
D["accumulating-snapshot"] = dict(items=[
    N("o", "order_date_key\nзаказ создан", 0, 0, "g", 260, 100),
    N("s", "shipped_date_key\nотгружен", 520, 0, "g", 260, 100),
    N("d", "delivered_date_key\nдоставлен", 1040, 0, "g", 260, 100),
    T("days_to_deliver = days_to_ship + days_in_transit.\nЭтап ещё не наступил: ключ даты = -1.", 260, 160, 20, "#1971c2"),
], edges=[E("o", "s", "days_to_ship"), E("s", "d", "days_in_transit")])

# ---- scd: типы
D["scd-types"] = dict(items=[
    N("q", "Клиент 79 переехал\nСанкт-Петербург → Казань\n16 февраля", 400, 0, "q", 400, 120),
    N("t0", "Type 0\nничего не меняем\nгород = Санкт-Петербург\nнавсегда", 0, 250, "n", 280, 150),
    N("t1", "Type 1\nперезаписываем\nгород = Казань\nистория потеряна", 310, 250, "r", 280, 150),
    N("t2", "Type 2\nновая строка\nв1: Санкт-Петербург (до 16.02)\nв2: Казань (с 16.02)", 620, 250, "g", 300, 150),
    N("t3", "Type 3\nновая колонка\ncity = Казань\nprevious_city = СПб", 950, 250, "y", 280, 150),
], edges=[E("q", "t0"), E("q", "t1"), E("q", "t2"), E("q", "t3")])

# ---- conformed: общие измерения
D["conformed-dimensions"] = dict(items=[
    N("fs", "fact_sales\nпродажи", 0, 60, "db", 280, 100),
    N("fi", "fact_inventory_daily\nостатки", 0, 330, "db", 280, 100),
    N("fr", "fact_returns\nвозвраты", 920, 190, "db", 280, 100),
    N("c", "dim_customer", 480, 0, "p", 240, 80), N("d", "dim_date", 480, 150, "p", 240, 80),
    N("p", "dim_product", 480, 300, "p", 240, 80), N("s", "dim_store", 480, 450, "p", 240, 80),
    T("Одни ключи, одни названия, одни значения атрибутов для всех фактов.", 200, 580),
], edges=[E(f, d, head=False) for f, d in [
    ("fs", "c"), ("fs", "d"), ("fs", "p"), ("fs", "s"), ("fi", "d"), ("fi", "p"), ("fi", "s"),
    ("fr", "c"), ("fr", "d"), ("fr", "p"), ("fr", "s")]])

# ---- conformed: drill-across
D["drill-across"] = dict(items=[
    N("fs", "fact_sales", 0, 0, "db", 280, 80), N("fi", "fact_inventory_daily", 400, 0, "db", 280, 80),
    N("as", "Шаг 1. Агрегируем\nпродажи по товару", 0, 170, "pu", 280, 100),
    N("ai", "Шаг 1. Агрегируем\nостатки по товару", 400, 170, "pu", 280, 100),
    N("j", "Шаг 2. JOIN двух результатов\nпо conformed dimension\n(product_key)", 140, 370, "p", 400, 120),
    N("r", "Отчёт: продажи и остатки\nв одной строке на товар", 140, 580, "g", 400, 100),
    T("Нельзя: JOIN двух fact tables напрямую.\nСтроки размножатся (fan-out).", 720, 190, 18, "#e03131"),
], edges=[E("fs", "as"), E("fi", "ai"), E("as", "j"), E("ai", "j"), E("j", "r")])

# ---- other-approaches: слои хранилища
D["architecture-layers"] = dict(items=[
    N("src", "Источники\nOLTP-базы, API, файлы", 0, 0, "n", 380, 100),
    N("stg", "Staging / raw (bronze)\nкопия источника как есть", 0, 180, "db", 380, 100),
    N("core", "Core / integration (silver)\nчистые данные: 3NF (Инмон)\nили Data Vault", 0, 360, "pu", 380, 130),
    N("mart", "Marts (gold)\nstar schema по Кимбаллу\nfacts + conformed dimensions", 0, 570, "g", 380, 130),
    N("obt", "OBT / wide tables\nдля дашбордов и ML", 480, 720, "y", 320, 100),
    N("bi", "BI, отчёты, AI-агенты", 0, 900, "p", 380, 90),
    T("Medallion — это слои,\nа не модель данных.", 480, 400, 18, "#868e96"),
], edges=[E("src", "stg"), E("stg", "core"), E("core", "mart"), E("mart", "obt"), E("mart", "bi"), E("obt", "bi")])

if __name__ == "__main__":
    names = sys.argv[1:] or list(D)
    OUT.mkdir(parents=True, exist_ok=True)
    for n in names:
        run(n, D[n])
