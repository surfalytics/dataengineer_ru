#!/usr/bin/env python3
"""Build the non-ER book diagrams in Excalidraw (needs the local canvas server on :3456).
Each diagram is a small spec (nodes at x/y, edges). Output: public/assets/data-warehouse-toolkit/<name>.png
Scenes are saved as dataengineer_ru/dwt-<name> in ~/dev/excalidraw/diagrams.
Usage: excalidraw_build.py [name ...]   (no args = all)"""
import base64, json, subprocess, sys, time, urllib.error, urllib.request
from pathlib import Path

API = "http://127.0.0.1:3456"
OUT = Path(__file__).resolve().parents[2] / "public/assets/data-warehouse-toolkit"
STYLE = {  # fill, stroke
    "p": ("#a5d8ff", "#1971c2"), "g": ("#b2f2bb", "#2f9e44"), "r": ("#ffc9c9", "#e03131"),
    "y": ("#ffec99", "#f08c00"), "db": ("#99e9f2", "#0c8599"), "q": ("#ffd8a8", "#e8590c"),
    "n": ("#e9ecef", "#868e96"), "pu": ("#eebefa", "#9c36b5"),
}
W, H, FONT = 250, 100, 20

LOCK = Path.home() / "dev/excalidraw/.canvas.lock"  # shared by every build script that draws on the canvas

class canvas_lock:
    """Cross-process lock: only one script draws on the shared canvas at a time."""
    def __enter__(self):
        import fcntl
        LOCK.parent.mkdir(parents=True, exist_ok=True)
        self.f = open(LOCK, "w")
        t0 = time.time()
        while True:
            try:
                fcntl.flock(self.f, fcntl.LOCK_EX | fcntl.LOCK_NB); break
            except BlockingIOError:
                if time.time() - t0 > 300: raise SystemExit("canvas lock busy for 5 min")
                time.sleep(1)
        return self
    def __exit__(self, *a):
        self.f.close()

def call(path, payload=None, method="POST"):
    req = urllib.request.Request(API + path, data=None if method == "GET" else json.dumps(payload or {}).encode(),
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
    scene = f"dataengineer_ru/dwt-{name}"
    with canvas_lock():
        prev = call("/api/scenes", method="GET").get("current")
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
        if prev and prev != scene: call("/api/scenes/open", {"name": prev})
    subprocess.run(["node", "-e",
        "const s=require('sharp'),fs=require('fs');const p=process.argv[1];"
        "s(p).resize({width:1600,withoutEnlargement:true}).png({palette:true,quality:90,compressionLevel:9})"
        ".toBuffer().then(b=>fs.writeFileSync(p,b))", str(raw)], check=True,
        cwd=Path(__file__).resolve().parents[2])
    print("ok", name, raw.stat().st_size)

def col(i): return i * 300
def row(j): return j * 150
D = {}

# ---- ch01
D["ch01-kimball-architecture"] = dict(items=[
    Z("Источники", -20, -60, 300, 520), Z("Back room: ETL system", 320, -60, 300, 520),
    Z("Presentation area", 660, -60, 340, 520), Z("Front room: BI", 1040, -60, 300, 520),
    N("s1", "ERP / POS", 10, 20, "n", 240), N("s2", "CRM", 10, 190, "n", 240), N("s3", "Файлы и API", 10, 360, "n", 240),
    N("e1", "Extract", 350, 20, "pu", 240), N("e2", "Clean\nи conform", 350, 190, "pu", 240), N("e3", "Deliver", 350, 360, "pu", 240),
    N("p1", "Star schemas\nпо бизнес-процессам", 690, 60, "g", 280, 110),
    N("p2", "Atomic grain +\nconformed dimensions", 690, 290, "g", 280, 110),
    N("b1", "Отчёты\nи дашборды", 1070, 60, "p", 240, 110), N("b2", "Ad hoc SQL", 1070, 290, "p", 240, 110),
], edges=[E("s1","e1"),E("s2","e1"),E("s3","e1"),E("e1","e2"),E("e2","e3"),E("e3","p1"),
          E("p1","p2",head=False),E("p1","b1"),E("p1","b2")])

# ---- ch02
D["ch02-fact-table-types"] = dict(items=[
    N("m", "Измерение\nбизнес-процесса", 540, 0, "n", 280, 100),
    N("t", "Transaction\nстрока = событие", 0, 200, "p", 280, 110), N("p", "Periodic snapshot\nстрока = период", 320, 200, "g", 280, 110),
    N("a", "Accumulating snapshot\nстрока = жизнь процесса", 640, 200, "y", 280, 110), N("f", "Factless\nстрока без чисел", 960, 200, "pu", 280, 110),
    N("t1", "Только insert.\nСтроки не меняются.\nНет события = нет строки", 0, 400, "p", 280, 130),
    N("p1", "Плотная: строка есть\nдаже без активности", 320, 400, "g", 280, 130),
    N("a1", "Строка обновляется:\nнесколько дат + lags", 640, 400, "y", 280, 130),
    N("f1", "Событие: кто пришёл.\nПокрытие: что могло\nбыть, но НЕ случилось", 960, 400, "pu", 280, 130),
], edges=[E("m","t"),E("m","p"),E("m","a"),E("m","f"),E("t","t1"),E("p","p1"),E("a","a1"),E("f","f1")])

# ---- ch04
D["ch04-inventory-pipeline"] = dict(items=[
    N("a", "Receipt\nприёмка", 0, 0, "p", 260), N("b", "Inspection\nпроверка", 0, 190, "p", 260),
    N("c", "Bin placement\nна склад", 0, 380, "p", 260), N("d", "First sale\nпервая продажа", 0, 570, "g", 260),
    T("Одна строка = одна партия (lot).\nСтрока обновляется на каждой вехе.", 320, 300, 18, "#1971c2"),
], edges=[E("a","b","lag 1"),E("b","c","lag 2"),E("c","d","lag 3")])

# ---- ch05
D["ch05-scd-types"] = dict(items=[
    N("q", "Атрибут изменился.\nНужна ли история?", 440, 0, "q", 360, 170, "diamond"),
    N("t0", "Type 0\nоставить как есть\n(не меняется)", 0, 360, "n", 230, 120), N("t1", "Type 1\nперезаписать\n(нужно только\nтекущее)", 250, 360, "p", 230, 120),
    N("t2", "Type 2\nновая строка\n(вся история)", 500, 360, "g", 230, 120), N("t3", "Type 3\nновая колонка\n(только\nпредыдущее)", 750, 360, "y", 230, 120),
    N("t4", "Type 4\nmini-dimension\n(часто меняется)", 1000, 360, "pu", 230, 120),
    N("h7", "Type 7\nдве dimension:\nType 1 и Type 2", 250, 600, "n", 230, 120),
    N("h6", "Type 6\nType 2 + колонки\nType 1", 500, 600, "n", 230, 120),
    N("h5", "Type 5\nmini-dimension +\nType 1 outrigger", 1000, 600, "n", 230, 120),
    T("Гибриды:", 20, 640, 22, "#495057"),
], edges=[E("q","t0"),E("q","t1"),E("q","t2"),E("q","t3"),E("q","t4"),E("t1","h7"),E("t2","h7"),E("t2","h6"),E("t4","h5")])

# ---- ch06
D["ch06-order-pipeline"] = dict(items=[
    N("o", "Order\nзаказ", 0, 0, "p", 260), N("s", "Shipment\nотгрузка", 0, 190, "p", 260),
    N("d", "Delivery\nдоставка", 0, 380, "p", 260), N("i", "Invoice\nсчёт", 0, 570, "g", 260),
    T("Одна строка на строку заказа.\nНа каждой вехе заполняется\nсвоя дата.", 320, 290, 18, "#1971c2"),
], edges=[E("o","s","order_to_ship_days"),E("s","d","ship_to_delivery_days"),E("d","i")])

# ---- ch07
D["ch07-budget-chain"] = dict(items=[
    N("c", "Commitment\nзаказы и обязательства", 0, 0, "p", 280), N("p", "Payment\nплатежи", 340, 0, "p", 280),
    N("j", "GL journal\nпроводки (atomic)", 680, 0, "p", 280),
    N("b", "Budget\nмесяц × отдел × счёт", 0, 190, "y", 280, 110), N("s", "GL snapshot\nостатки на конец периода", 680, 190, "p", 280, 110),
    N("v", "Variance\nconsolidated fact", 340, 380, "g", 280), N("r", "Отчёт:\nплан vs факт", 680, 380, "g", 280),
], edges=[E("b","c"),E("c","p"),E("p","j"),E("j","s"),E("b","v"),E("s","v"),E("v","r")])

# ---- ch11
_before = ["Grain: один счёт\nв месяц", "Bill dimension с\nмиллионами строк", "Дата счёта не\nсвязана с dimension",
           "Sales channel\nв snowflake", "Текстовый код\nтарифа в fact", "Ключи из источника", "YTD в fact", "Только коды,\nбез названий"]
_after = ["Grain: линия на счёте", "Bill number как\ndegenerate dimension", "Дата в fact:\nроль bill date",
          "Channel внутри\nsales org", "Код и описание\nв rate plan", "Surrogate keys везде", "YTD считает запрос", "Понятные описания"]
D["ch11-design-review"] = dict(items=[
    Z("Было в черновике", -20, -60, 400, 1140), Z("Стало после ревью", 440, -60, 440, 1140),
] + [N(f"b{i}", t, 0, 20 + i * 130, "r", 360, 100) for i, t in enumerate(_before)]
  + [N(f"a{i}", t, 480, 20 + i * 130, "g", 360, 100) for i, t in enumerate(_after)],
  edges=[E(f"b{i}", f"a{i}") for i in range(8)])

# ---- ch12
D["ch12-flight-grains"] = dict(items=[
    N("i", "Itinerary\nвесь билет", 0, 0, "n"), N("t", "Trip\nпоездка от A до B", 0, 160, "p"),
    N("s", "Segment\nодин flight number,\nодин самолёт", 0, 320, "p", 250, 120), N("l", "Leg\nодин взлёт и\nодна посадка", 0, 500, "p", 250, 120),
    N("f3", "trip summary\naggregate, по желанию", 380, 160, "y", 280), N("f1", "fact_segment_flight\nвыручка и мили", 380, 330, "g", 280),
    N("f2", "fact_leg_flight\nзадержки по плечам", 380, 510, "g", 280),
], edges=[E("i","t"),E("t","s"),E("s","l"),E("t","f3",dashed=True),E("s","f1",dashed=True),E("l","f2",dashed=True)])

# ---- ch13
D["ch13-applicant-pipeline"] = dict(items=[
    N("a", "Inquiry\nзапрос", 0, 0), N("b", "Campus visit\nвизит", 0, 150), N("c", "Application submitted\nзаявка подана", 0, 300),
    N("d", "File completed\nдокументы собраны", 0, 450), N("e", "Decision\nрешение комиссии", 0, 600), N("f", "Enrolled\nзачислен", 0, 750, "g"),
    N("r", "fact_applicant_pipeline\nодна строка на абитуриента,\nдата каждого шага,\nстрока обновляется", 460, 270, "db", 330, 220),
], edges=[E("a","b"),E("b","c"),E("c","d"),E("d","e"),E("e","f")]+[E(x,"r",dashed=True) for x in "abcdef"])

# ---- ch14
D["ch14-claim-workflow"] = dict(items=[
    N("a", "Treatment\nлечение", 0, 0), N("b", "Bill primary insurance\nсчёт первичной страховой", 0, 150, "p", 290),
    N("c", "Bill secondary insurance\nсчёт вторичной страховой", 0, 300, "p", 290),
    N("d", "Bill responsible party\nсчёт пациенту", 0, 450, "p", 290),
    N("e", "Last payments\nпоследние оплаты\nкаждой из трёх сторон", 0, 600, "p", 290, 120),
    N("f", "Zero balance\nдолг закрыт", 0, 780, "g", 290),
    N("r", "fact_claim_line\nодна строка на строку счёта,\nроль даты на каждый этап,\nстрока обновляется", 480, 290, "db", 340, 220),
], edges=[E("a","b"),E("b","c"),E("c","d"),E("d","e"),E("e","f")]+[E(x,"r",dashed=True) for x in "abcdef"])

# ---- ch15
D["ch15-clickstream-flow"] = dict(items=[
    N("l", "Web log\nодин hit = одна строка", 0, 0, "n", 280), N("s", "Sessionization\nпауза > 30 минут =\nновая сессия", 340, 0, "y", 280, 120),
    N("p", "fact_page_event\ngrain: событие страницы", 680, 0, "db", 300, 120),
    N("f", "fact_session\ngrain: одна сессия", 680, 200, "db", 300, 110), N("a", "aggregate\nмесяц, сегмент, исход", 680, 400, "db", 300, 110),
    N("d", "Conformed dimensions\nдата, страница,\nreferrer, клиент", 300, 200, "pu", 320, 130),
], edges=[E("l","s"),E("s","p"),E("p","f"),E("f","a"),E("d","p",dashed=True),E("d","f",dashed=True),E("d","a",dashed=True)])

# ---- ch16
D["ch16-premium-example"] = dict(items=[
    N("t1", "Январь: полис на год\ntransaction +600", 0, 0, "p", 280), N("t2", "31 марта: отмена\ntransaction -450", 0, 380, "r", 280),
    N("w1", "written premium\nянварь: 600", 380, 0, "g", 260), N("e", "earned premium\n50 в месяц:\nянварь, февраль, март", 380, 160, "g", 260, 130),
    N("w2", "written premium\nмарт: -450", 380, 380, "g", 260),
    N("s", "fact_premium_snapshot\nполис × покрытие ×\nобъект × месяц", 740, 170, "db", 300, 120),
], edges=[E("t1","w1"),E("t1","e"),E("t2","e"),E("t2","w2"),E("w1","s"),E("e","s"),E("w2","s")])

# ---- ch17
D["ch17-lifecycle"] = dict(items=[
    N("plan", "Планирование\nпрограммы и проекта", 330, 0, "p", 260), N("req", "Определение\nбизнес-требований", 330, 150, "p", 260),
    N("pm", "Управление программой\nи проектом:\nидёт всё время", 700, 0, "y", 300, 130),
    N("t1", "Техническая\nархитектура", 0, 330, "pu", 240), N("t2", "Выбор и установка\nпродуктов", 0, 480, "pu", 240),
    N("d1", "Dimensional\nmodeling", 330, 330, "g", 260), N("d2", "Физический дизайн", 330, 480, "g", 260), N("d3", "Дизайн и разработка\nETL", 330, 630, "g", 260),
    N("b1", "Дизайн\nBI-приложений", 680, 330, "p", 240), N("b2", "Разработка\nBI-приложений", 680, 480, "p", 240),
    N("dep", "Развёртывание", 330, 810, "n", 260), N("m", "Сопровождение", 330, 950, "n", 260),
    N("gr", "Рост:\nновый проект =\nновый цикл", 330, 1090, "y", 260, 110),
], edges=[E("plan","req"),E("req","t1"),E("req","d1"),E("req","b1"),E("t1","t2"),E("d1","d2"),E("d2","d3"),E("b1","b2"),
          E("t2","dep"),E("d3","dep"),E("b2","dep"),E("dep","m"),E("m","gr")])

# ---- ch18 bubble chart
left = ["Order Date", "Due Date", "Sold To Customer", "Ship To Customer", "Bill To Customer", "Currency"]
right = ["Product", "Promotion", "Channel", "Sales Person", "Order Profile\n(junk dimension)"]
D["ch18-bubble-chart"] = dict(items=[
    N("f", "Orders\ngrain: 1 строка\nна строку заказа", 410, 220, "p", 300, 240, "ellipse"),
] + [N(f"l{i}", t, 0, i * 130, "n", 250, 90) for i, t in enumerate(left)]
  + [N(f"r{i}", t, 870, 65 + i * 130, "g" if i == 4 else "n", 250, 90) for i, t in enumerate(right)],
  edges=[E(f"l{i}", "f", head=False) for i in range(len(left))] + [E("f", f"r{i}", head=False) for i in range(5)])

# ---- ch18 process
D["ch18-modeling-process"] = dict(items=[
    N("a", "1. Подготовка\nучастники, инструменты,\nnaming, календарь", 0, 0, "p", 330, 120),
    N("b", "2. High-level модель\n(bubble chart):\ngrain и dimensions", 0, 170, "p", 330, 120),
    N("c", "3. Детальная модель\ndimensions, facts, SCD,\nправила ETL", 0, 340, "p", 330, 120),
    N("d", "4. Итерации и тесты\nна требованиях\nи данных", 0, 510, "y", 330, 120),
    N("e", "5. Review\nIT, core users, бизнес", 0, 680, "y", 330, 120),
    N("f", "6. Финальная\nдокументация", 0, 850, "g", 330, 120),
    T("← нашли проблему:\nвернуться к шагу 2", 370, 540, 20, "#e8590c"),
    T("← правки:\nвернуться к шагу 3", 370, 710, 20, "#e8590c"),
], edges=[E("a","b"),E("b","c"),E("c","d"),E("d","e"),E("e","f")])

# ---- ch19
D["ch19-etl-subsystems"] = dict(items=[
    N("src", "Источники", 0, 0, "n", 330, 80),
    N("e", "EXTRACT\n1 Data profiling\n2 CDC\n3 Extract", 0, 140, "p", 330, 140),
    N("c", "CLEAN и CONFORM\n4 Cleansing\n5 Error event schema\n6 Audit dimension\n7 Deduplication\n8 Conforming", 0, 340, "g", 330, 220),
    N("d", "DELIVER\n9-13: SCD, surrogate keys,\nиерархии, special dimensions,\nfact builders\n14-16: SK pipeline,\nmultivalued, late arriving\n17-21: dimension manager,\nfact provider, aggregates,\ncubes, propagation", 0, 620, "pu", 330, 290),
    N("p", "Presentation area", 0, 970, "db", 330, 80),
    N("m", "MANAGE\n22-34: scheduler, backup,\nrecovery, versioning,\nmonitor, sorting, lineage,\nescalation, parallelizing,\nsecurity, compliance,\nmetadata", 520, 330, "y", 360, 270),
], edges=[E("src","e"),E("e","c"),E("c","d"),E("d","p"),E("m","e",dashed=True),E("m","c",dashed=True),E("m","d",dashed=True)])

# ---- ch20
D["ch20-incremental-etl"] = dict(items=[
    N("s", "Source", 0, 0, "db", 260, 80), N("st", "Staging\nкопия сырых данных", 0, 140, "p", 260),
    N("q", "Quality\nscreens", 0, 300, "q", 260, 150, "diamond"),
    N("err", "Error event\nстрока идёт дальше\nили помечается", 480, 310, "r", 260, 120), N("dim", "Dimensions:\nSCD 1 и 2", 0, 510, "p", 260),
    N("sk", "Surrogate key\npipeline", 0, 670, "p", 260), N("unk", "Inferred member\n(лучше по книге)\nили unknown", 480, 660, "y", 260, 120),
    N("f", "Fact table\ndelete + insert", 0, 830, "db", 260), N("aud", "Audit и\nreconciliation", 0, 990, "p", 260),
    N("hwm", "Обновить HWM", 0, 1130, "g", 260, 80),
], edges=[E("s","st","modified_at > HWM"),E("st","q"),E("q","err","ошибка: записать событие"),E("q","dim","дальше"),E("dim","sk"),
          E("sk","unk","нет ключа"),E("sk","f"),E("f","aud"),E("aud","hwm")])

# ---- ch21
D["ch21-data-highway"] = dict(items=[
    N("raw", "Raw source\nсразу", 0, 0, "r", 260), N("rt", "Real time cache\nсекунды", 0, 150, "p", 260),
    N("ba", "Business activity cache\nминуты", 0, 300, "p", 260), N("tl", "Top line cache\n24 часа", 0, 450, "p", 260),
    N("dw", "DW и long time series\nдень, период, год", 0, 600, "g", 260),
    N("bf", "backflow:\ndurable keys, итоги", 420, 300, "y", 260),
], edges=[E("raw","rt"),E("rt","ba"),E("ba","tl"),E("tl","dw"),E("dw","bf",dashed=True),
          E("bf","tl",dashed=True),E("bf","ba",dashed=True),E("bf","rt",dashed=True)])

# ---- overview: book map
D["book-map"] = dict(items=[
    N("p1", "Часть 1\nОсновы\nглавы 1–2", 0, 0, "p", 270, 120),
    N("p2", "Часть 2\nБизнес-процессы\nглавы 3–9", 320, 0, "g", 270, 120),
    N("p3", "Часть 3\nОтрасли\nглавы 10–16", 640, 0, "g", 270, 120),
    N("p4", "Часть 4\nПроект и ETL\nглавы 17–20", 960, 0, "pu", 270, 120),
    N("p5", "Часть 5\nBig data\nглава 21", 1280, 0, "y", 270, 120),
    N("d1", "Цели DW/BI,\nstar schema,\nсправочник приёмов", 0, 230, "n", 270, 120),
    N("d2", "grain, bus matrix,\nSCD, три вида\nfact table", 320, 230, "n", 270, 120),
    N("d3", "bridge, supertype,\nclickstream,\nстрахование", 640, 230, "n", 270, 120),
    N("d4", "Lifecycle, workshops,\n34 подсистемы ETL,\n10 шагов разработки", 960, 230, "n", 270, 120),
    N("d5", "RDBMS и Hadoop,\nbest practices", 1280, 230, "n", 270, 120),
], edges=[E("p1","p2"),E("p2","p3"),E("p3","p4"),E("p4","p5"),
          E("p1","d1",head=False),E("p2","d2",head=False),E("p3","d3",head=False),
          E("p4","d4",head=False),E("p5","d5",head=False)])

if __name__ == "__main__":
    names = sys.argv[1:] or list(D)
    OUT.mkdir(parents=True, exist_ok=True)
    for n in names:
        run(n, D[n])
