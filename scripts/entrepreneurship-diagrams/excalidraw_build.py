#!/usr/bin/env python3
"""Build diagrams for the entrepreneurship book summaries in Excalidraw (needs the local canvas server on :3456).
Each diagram is a small spec (nodes at x/y, edges). Key = "<book-slug>/<name>".
Output: public/assets/<book-slug>/<name>.png
Scenes are saved as dataengineer_ru/<prefix>-<name> in ~/dev/excalidraw/diagrams.
Usage: excalidraw_build.py [key ...]   (no args = all)"""
import base64, json, subprocess, sys, time, urllib.error, urllib.request
from pathlib import Path

API = "http://127.0.0.1:3456"
ROOT = Path(__file__).resolve().parents[2]
PREFIX = {"startup-owners-manual": "som", "mom-test": "mom", "diary-of-a-ceo": "doac"}
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

def run(key, spec):
    book, name = key.split("/")
    scene = f"dataengineer_ru/{PREFIX[book]}-{name}"
    out = ROOT / "public/assets" / book
    out.mkdir(parents=True, exist_ok=True)
    with canvas_lock():
        els = build(spec)
        prev = call("/api/scenes", method="GET").get("current")
        for attempt in range(8):  # another session may use the same canvas: verify scene and count, retry
            try:
                call("/api/scenes", {"name": scene})
            except urllib.error.HTTPError as e:  # scene exists (re-run): reopen
                if e.code != 409: raise
                call("/api/scenes/open", {"name": scene})
            if call("/api/scenes", method="GET").get("current") != scene: continue
            call("/api/elements/clear", method="DELETE")
            call("/api/elements/batch", {"elements": els})
            got = call("/api/elements", method="GET")["elements"]
            cur = call("/api/scenes", method="GET").get("current")
            if cur == scene and len(got) == len(els):
                r = call("/api/export/image", {"format": "png", "scale": 2, "padding": 30})
                if call("/api/scenes", method="GET").get("current") == scene: break
            time.sleep(2)
        else:
            raise SystemExit(f"canvas busy, could not build {key}")
        raw = out / f"{name}.png"
        raw.write_bytes(base64.b64decode(r["data"]))
        call("/api/scenes/save")
        if prev and prev != scene:  # give the canvas back to whoever had it
            call("/api/scenes/open", {"name": prev})
    subprocess.run(["node", "-e",
        "const s=require('sharp'),fs=require('fs');const p=process.argv[1];"
        "s(p).resize({width:1600,withoutEnlargement:true}).png({palette:true,quality:90,compressionLevel:9})"
        ".toBuffer().then(b=>fs.writeFileSync(p,b))", str(raw)], check=True,
        cwd=ROOT)
    print("ok", key, raw.stat().st_size)

D = {}
# ---------- The Mom Test
D["mom-test/ch01-mom-test-rules"] = dict(items=[
    N("t", "Тест мамы", 380, 0, "q", 300, 90),
    N("r1", "1. Говорите о жизни\nклиента\n(не о своей идее)", 0, 180, "p", 320, 130),
    N("r2", "2. Спрашивайте о\nконкретном прошлом\n(не о будущем)", 370, 180, "p", 320, 130),
    N("r3", "3. Меньше говорите,\nбольше слушайте\n(не продавайте)", 740, 180, "p", 320, 130),
    N("res", "Результат: факты,\nа не комплименты", 370, 400, "g", 320, 100),
], edges=[E("t","r1"),E("t","r2"),E("t","r3"),E("r1","res"),E("r2","res"),E("r3","res")])

D["mom-test/ch02-bad-data"] = dict(items=[
    T("Плохие данные", 0, -50, 22, "#e03131"), T("Что делать", 480, -50, 22, "#2f9e44"),
    N("b1", "Комплименты\n«Классная идея!»", 0, 0, "r", 340, 110), N("a1", "Отклонить и вернуть\nк фактам", 480, 0, "g", 340, 110),
    N("b2", "Fluff: «обычно»,\n«я бы», «может быть»", 0, 170, "r", 340, 110), N("a2", "Заземлить:\n«Когда это было\nпоследний раз?»", 480, 170, "g", 340, 110),
    N("b3", "Идеи и запросы\nфич", 0, 340, "r", 340, 110), N("a3", "Раскопать:\n«Зачем вам это?»", 480, 340, "g", 340, 110),
    N("goal", "Цель: факты\nи обязательства", 960, 170, "p", 280, 110),
], edges=[E("b1","a1"),E("b2","a2"),E("b3","a3"),E("a1","goal"),E("a2","goal"),E("a3","goal")])

D["mom-test/ch05-commitment"] = dict(items=[
    N("m", "Конец встречи", 380, 0, "n", 320, 80),
    N("o1", "Шаг вперёд\n(advancement):\nуспех", 0, 160, "g", 320, 120),
    N("o2", "Ясный отказ:\nтоже знание", 380, 160, "y", 320, 120),
    N("o3", "Комплимент без шага:\nzombie lead, провал", 760, 160, "r", 320, 120),
    Z("Валюты обязательств", -20, 340, 360, 440),
    N("c1", "Время: встреча,\nфидбэк, пилот", 0, 400, "p", 320, 100),
    N("c2", "Репутация:\nзнакомство, отзыв", 0, 530, "p", 320, 100),
    N("c3", "Деньги: предзаказ,\nдепозит", 0, 660, "p", 320, 100),
], edges=[E("m","o1"),E("m","o2"),E("m","o3"),E("o1","c1")])

D["mom-test/ch08-process"] = dict(items=[
    Z("До", -20, -60, 700, 220), N("b1", "Сегмент и\n3 главных вопроса", 0, 0, "p", 300, 100), N("b2", "Какое обязательство\nпросить", 360, 0, "p", 300, 100),
    Z("Во время", -20, 240, 700, 220), N("d1", "Тест мамы,\nлёгкий тон", 0, 300, "p", 300, 100), N("d2", "Заметки и\nобязательство", 360, 300, "p", 300, 100),
    Z("После", -20, 540, 700, 220), N("a1", "Разбор с командой", 0, 600, "g", 300, 100), N("a2", "Обновить убеждения\nи 3 вопроса", 360, 600, "g", 300, 100),
    N("n", "Следующий\nразговор", 820, 300, "y", 240, 100),
], edges=[E("b1","b2"),E("b1","d1"),E("d1","d2"),E("d1","a1"),E("a1","a2"),E("a2","n"),E("n","b2",dashed=True)])

# ---------- The Startup Owner's Manual (9, 13, 14)
D["startup-owners-manual/ch09-customer-validation-phases"] = dict(items=[
    T("Цель: повторяемые и масштабируемые продажи", 0, -60, 22, "#1971c2"),
    N("p1", "Фаза 1\nПодготовка к продажам", 0, 0, "p", 320, 100),
    N("p2", "Фаза 2\nВыйти и продавать", 0, 160, "p", 320, 100),
    N("p3", "Фаза 3\nПозиционирование", 0, 320, "p", 320, 100),
    N("p4", "Фаза 4\nPivot or proceed?", -20, 480, "q", 360, 170, "diamond"),
    N("pv", "Pivot:\nназад в\ncustomer discovery", 480, 515, "r", 280, 110),
    N("pr", "Proceed:\ncustomer creation", 0, 730, "g", 320, 100),
], edges=[E("p1","p2"),E("p2","p3"),E("p3","p4"),E("p4","pv","нет"),E("p4","pr","да")])

D["startup-owners-manual/ch13-pivot-or-proceed"] = dict(items=[
    N("a", "Собрать данные\n(war room)", 0, 0, "n", 320, 90),
    N("b", "Проверить\nбизнес-модель", 0, 150, "p", 320, 90),
    N("c", "Проверить финансы\n(metrics that matter)", 0, 300, "p", 320, 100),
    N("w", "Деньги кончатся\nза год? Стоп", 470, 300, "y", 280, 100),
    N("q", "Мнения стали\nфактами? Рост\nпредсказуем?", -30, 470, "q", 380, 190, "diamond"),
    N("p1", "Pivot:\nназад в фазу 1\nvalidation", 470, 420, "y", 280, 110),
    N("p2", "Pivot:\nназад в\ncustomer discovery", 470, 580, "r", 280, 110),
    N("ok", "Proceed:\ncustomer creation", 0, 740, "g", 320, 100),
], edges=[E("a","b"),E("b","c"),E("c","w",dashed=True),E("c","q"),E("q","p1","не предсказуем"),E("q","p2","глубже"),E("q","ok","да")])

_s = ["1. Команда", "2. Гипотезы canvas", "3. Фраза о ценности", "4. Домен и хостинг", "5. Low-fidelity сайт",
      "6. Трафик на сайт", "7. Backend", "8. Тест проблемы\nна данных", "9. High-fidelity сайт", "10. Попросить денег"]
D["startup-owners-manual/ch14-web-startup-steps"] = dict(items=[
    N(f"s{i}", t, (i if i < 5 else 9 - i) * 270, (i // 5) * 160, "g" if i == 9 else "p", 230, 90) for i, t in enumerate(_s)
] + [T("Каждую неделю: отчёт Lessons Learned", 0, 330, 20, "#f08c00")],
  edges=[E(f"s{i}", f"s{i+1}") for i in range(9)])
# ---------- SBM 1, 2, 4, 5
_pd = [("Идея", "n"), ("Разработка\nпродукта", "p"), ("Alpha / beta\nтест", "p"), ("Запуск и\nпродажи", "p"), ("Масштаб", "n")]
D["startup-owners-manual/ch01-product-development-model"] = dict(items=[
    N(f"s{i}", t, i * 290, 0, k, 250, 100) for i, (t, k) in enumerate(_pd)
] + [
    N("p1", "Нет шага:\nпроверить, что клиенты\nхотят продукт", 290, 220, "r", 300, 120),
    N("p2", "Деньги и время\nуходят до первых\nвыводов", 690, 220, "r", 300, 120),
    N("ok", "Стартапу нужен\nпоиск модели,\nа не план", 1090, 220, "y", 300, 120),
], edges=[E(f"s{i}", f"s{i+1}") for i in range(4)] + [E("s1","p1",dashed=True),E("s3","p2",dashed=True),E("p2","ok",dashed=True)])

D["startup-owners-manual/ch02-customer-development-model"] = dict(items=[
    Z("Поиск (search): модель — набор гипотез", -20, -60, 700, 400),
    Z("Исполнение (execution): модель проверена", -20, 400, 700, 220),
    N("d", "1. Customer\ndiscovery", 0, 20, "p", 280, 100), N("v", "2. Customer\nvalidation", 360, 20, "p", 280, 100),
    N("o", "Модель\nработает?", 360, 190, "q", 280, 110, "diamond"),
    N("pv", "Pivot: изменить\nгипотезы", 0, 200, "y", 280, 90),
    N("c", "3. Customer\ncreation", 0, 470, "g", 280, 100), N("b", "4. Company\nbuilding", 360, 470, "g", 280, 100),
], edges=[E("d","v"),E("v","o"),E("o","pv","нет"),E("pv","d"),E("o","c","да"),E("c","b")])

D["startup-owners-manual/ch04-customer-discovery-phases"] = dict(items=[
    N("p1", "Фаза 1\nСформулировать\nгипотезы модели", 0, 0, "p", 300, 130),
    N("p2", "Фаза 2\nПроверить проблему:\nоно им нужно?", 0, 190, "p", 300, 130),
    N("p3", "Фаза 3\nПроверить решение:\nпродукт подходит?", 0, 380, "p", 300, 130),
    N("p4", "Фаза 4\nПроверить модель:\npivot or proceed?", 0, 570, "q", 320, 130),
    N("ok", "Proceed:\ncustomer validation", 460, 570, "g", 300, 100),
    N("pv", "Pivot:\nменять гипотезы", 460, 380, "y", 300, 100),
    T("Выйти из офиса:\nговорить с клиентами", 460, 215, 20, "#1971c2"),
], edges=[E("p1","p2"),E("p2","p3"),E("p3","p4"),E("p4","ok","да"),E("p4","pv","нет"),E("pv","p1",dashed=True)])

D["startup-owners-manual/ch05-business-model-canvas"] = dict(items=[
    N("kp", "Партнёры", 0, 0, "n", 230, 250), N("ka", "Ключевые\nактивности", 250, 0, "p", 230, 120), N("kr", "Ресурсы", 250, 130, "p", 230, 120),
    N("vp", "Ценностное\nпредложение", 500, 0, "g", 250, 250),
    N("cr", "Отношения\nс клиентами", 770, 0, "pu", 230, 120), N("ch", "Каналы", 770, 130, "pu", 230, 120),
    N("cs", "Сегменты\nклиентов", 1020, 0, "y", 230, 250),
    N("co", "Издержки", 0, 270, "r", 615, 110), N("rv", "Выручка", 635, 270, "g", 615, 110),
], edges=[])

D["startup-owners-manual/ch05-get-keep-grow"] = dict(items=[
    N("g", "GET\nпривлечь\nweb: acquire, activate", 0, 0, "p", 300, 130),
    N("k", "KEEP\nудержать\nweb: retain", 380, 0, "g", 300, 130),
    N("r", "GROW\nвырастить\nweb: grow", 760, 0, "y", 300, 130),
    N("v", "Вирусная петля:\nклиент приводит\nновых клиентов", 380, 230, "pu", 300, 120),
    T("Три задачи отношений с клиентами", 0, -50, 22, "#495057"),
], edges=[E("g","k"),E("k","r"),E("r","v",dashed=True),E("v","g",dashed=True)])

# ---------- DOAC
D["diary-of-a-ceo/ch01-five-buckets"] = dict(items=[
    N("b1", "1. Знания", 0, 120, "g", 200, 90), N("b2", "2. Навыки", 250, 120, "g", 200, 90),
    N("b3", "3. Связи", 500, 120, "p", 200, 90), N("b4", "4. Ресурсы", 750, 120, "p", 200, 90), N("b5", "5. Репутация", 1000, 120, "p", 200, 90),
    T("Землетрясение не отнимет", 40, 40, 20, "#2f9e44"),
    N("tr", "Ловушка эго:\nпрыжок сразу к 4-5", 400, 300, "r", 380, 90),
], edges=[E("b1","b2"),E("b2","b3"),E("b3","b4"),E("b4","b5"),E("tr","b4",dashed=True)])

D["diary-of-a-ceo/ch08-habit-loop"] = dict(items=[
    N("c", "Сигнал (cue)", 0, 0, "p", 260, 90), N("r", "Действие (routine)", 380, 0, "p", 260, 90),
    N("w", "Награда (reward)", 190, 200, "g", 280, 90),
    N("n", "Замена: новое\nдействие, та же награда", 700, 200, "y", 300, 100),
    N("e", "Машина → сигарета →\nледенец", 700, 370, "n", 300, 90),
    T("Не боритесь с привычкой — заменяйте действие", 0, 340, 20, "#e8590c"),
], edges=[E("c","r"),E("r","w"),E("w","c",dashed=True),E("r","n",dashed=True),E("n","e",head=False)])

D["diary-of-a-ceo/ch13-psychological-moonshots"] = dict(items=[
    N("m", "Psychological moonshot:\nмалое изменение →\nбольшое восприятие", 380, 230, "q", 340, 140, "ellipse"),
    N("a", "Пик и конец", 0, 0, "p", 260, 80), N("b", "Неприятие\nожидания", 380, -20, "p", 260, 90),
    N("c", "Прозрачность\nпроцесса", 760, 0, "p", 260, 90),
    N("d", "Тревога\nнеизвестности", 60, 470, "p", 260, 90), N("e", "Близость цели", 700, 470, "p", 260, 80),
], edges=[E("a","m"),E("b","m"),E("c","m"),E("d","m"),E("e","m")])

D["diary-of-a-ceo/ch19-kaizen"] = dict(items=[
    N("s", "Старт: £100", 0, 150, "n", 220, 90),
    N("u", "+1% каждый день", 330, 20, "g", 260, 80), N("d", "-1% каждый день", 330, 280, "r", 260, 80),
    N("ur", "Через год:\n≈ £3 778 (×37)", 720, 10, "g", 260, 100), N("dr", "Через год:\n≈ £2,55", 720, 270, "r", 260, 100),
    T("Мелочи накапливаются", 330, 420, 22, "#495057"),
], edges=[E("s","u"),E("s","d"),E("u","ur"),E("d","dr")])

D["diary-of-a-ceo/ch21-pro-failure"] = dict(items=[
    N("a", "1. Убрать\nбюрократию", 0, 0, "p", 230, 100), N("b", "2. Исправить\nстимулы", 270, 0, "p", 230, 100),
    N("c", "3. Повышать\nи увольнять", 540, 0, "p", 230, 100), N("d", "4. Измерять\nточно", 810, 0, "p", 230, 100),
    N("e", "5. Делиться\nпровалами", 1080, 0, "p", 230, 100),
    N("r", "Провал → обратная связь → знание → сила", 270, 200, "g", 770, 80),
], edges=[E("a","b"),E("b","c"),E("c","d"),E("d","e"),E("e","r",dashed=True)])

D["diary-of-a-ceo/ch30-three-bars"] = dict(items=[
    T("Вопрос: если бы все были как он — планка выше или ниже?", 0, -50, 22, "#1971c2"),
    N("u", "Поднимает планку\n→ повышать", 0, 0, "g", 320, 100),
    N("m", "Планка команды (среднее)", 0, 160, "n", 320, 80),
    N("h", "Держит планку\n→ развивать", 0, 300, "y", 320, 100),
    N("l", "Опускает планку\n→ расставаться", 0, 460, "r", 320, 100),
], edges=[E("u","m",head=False),E("m","h",head=False),E("h","l",head=False)])

if __name__ == "__main__":
    keys = sys.argv[1:] or list(D)
    for k in keys:
        run(k, D[k])
