#!/usr/bin/env python3
"""Build the non-ER book diagrams in Excalidraw (needs the local canvas server on :3456).
Each diagram is a small spec (nodes at x/y, edges). Output: public/assets/machines-that-think/<name>.png
Scenes are saved as dataengineer_ru/mtt-<name> in ~/dev/excalidraw/diagrams.
Usage: excalidraw_build.py [name ...]   (no args = all)"""
import base64, json, subprocess, sys, time, urllib.error, urllib.request
from pathlib import Path

API = "http://127.0.0.1:3456"
OUT = Path(__file__).resolve().parents[2] / "public/assets/machines-that-think"
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

def current_scene():
    return json.load(urllib.request.urlopen(API + "/api/scenes", timeout=60))["current"]

def element_count():
    return json.load(urllib.request.urlopen(API + "/api/elements", timeout=60))["count"]

def draw(scene, spec):
    """Draw on a fresh scene. The canvas server is shared, so check that nothing else touched it."""
    try:
        call("/api/scenes", {"name": scene})
    except urllib.error.HTTPError as e:  # scene exists (re-run): reopen and clear it
        if e.code != 409: raise
        call("/api/scenes/open", {"name": scene})
        call("/api/elements/clear", method="DELETE")
    call("/api/elements/batch", {"elements": build(spec)})
    n = element_count()
    r = call("/api/export/image", {"format": "png", "scale": 2, "padding": 30})
    if current_scene() != scene or element_count() != n:
        return None  # another session used the canvas meanwhile
    return r

def run(name, spec):
    scene = f"dataengineer_ru/mtt-{name}"
    for attempt in range(5):
        r = draw(scene, spec)
        if r: break
        print("canvas busy, retry", name)
        time.sleep(5)
    else:
        raise SystemExit(f"cannot draw {name}: canvas is shared and busy")
    raw = OUT / f"{name}.png"
    raw.write_bytes(base64.b64decode(r["data"]))
    call("/api/scenes/save")
    subprocess.run(["node", "-e",
        "const s=require('sharp'),fs=require('fs');const p=process.argv[1];"
        "s(p).resize({width:1600,withoutEnlargement:true}).png({palette:true,quality:90,compressionLevel:9})"
        ".toBuffer().then(b=>fs.writeFileSync(p,b))", str(raw)], check=True,
        cwd=Path(__file__).resolve().parents[2])
    print("ok", name, raw.stat().st_size)


D = {}

# ---- ch01
D["ch01-ai-history"] = dict(items=[
    N("a", "Мифы и автоматы\nмеханические\nиллюзии", 0, 0, "n", 230, 110),
    N("b", "Логика Буля,\nмашина Бэббиджа", 290, 0, "n", 230, 110),
    N("c", "Машина Тьюринга\nи тест\nимитации", 580, 0, "p", 230, 110),
    N("d", "Символьный ИИ\nправила вручную", 870, 0, "pu", 230, 110),
    N("e", "Правила ломаются\nна реальном мире", 870, 220, "r", 230, 110),
    N("f", "Вероятностные\nмодели и\nобучение на данных", 580, 220, "p", 230, 110),
    N("g", "Нейросети\nи масштаб", 290, 220, "g", 230, 110),
    N("h", "LLM", 0, 220, "g", 230, 110),
    N("n", "Цикл: подъём, разочарование, зима, новый подъём", 290, 400, "y", 520, 80),
], edges=[E("a","b"),E("b","c"),E("c","d"),E("d","e"),E("e","f"),E("f","g"),E("g","h"),E("e","n",dashed=True)])

# ---- ch02
D["ch02-language-pipeline"] = dict(items=[
    N("r", "Правила\nграмматика\nвручную", 0, 0, "n", 230, 110),
    N("ng", "n-gram\nподсчёт слов,\nпроблема sparsity", 290, 0, "p", 230, 110),
    N("tk", "Токены\nBPE, subword", 580, 0, "pu", 230, 110),
    N("oh", "One-hot\nвектор огромный,\nсмысла нет", 580, 220, "r", 230, 110),
    N("se", "Статические\nembeddings\nодно слово — один вектор", 290, 220, "g", 230, 110),
    N("ce", "Контекстные\nembeddings\nсмысл зависит от фразы", 0, 220, "g", 230, 110),
    N("n", "Язык остаётся трудным: контекст, неявный смысл, разные языки", 0, 400, "y", 810, 80),
], edges=[E("r","ng"),E("ng","tk"),E("tk","oh"),E("oh","se"),E("se","ce"),E("ce","n",dashed=True)])

# ---- ch03
D["ch03-training-loop"] = dict(items=[
    N("x", "Данные\nвход + верный ответ", 0, 0, "n", 250, 100),
    N("fw", "Forward pass\nсеть даёт прогноз", 330, 0, "p", 250, 100),
    N("ls", "Loss\nнасколько ошиблись", 660, 0, "r", 250, 100),
    N("bp", "Backpropagation\nвклад каждого веса", 660, 200, "pu", 250, 100),
    N("gd", "Gradient descent\nчуть сдвинуть веса", 330, 200, "g", 250, 100),
    N("st", "Хватит?\nearly stopping", 0, 190, "q", 250, 120, "diamond"),
    N("ov", "Overfitting:\nсеть заучила данные", 330, 380, "y", 250, 100),
], edges=[E("x","fw"),E("fw","ls"),E("ls","bp"),E("bp","gd"),E("gd","st"),E("st","fw","нет"),E("st","ov","да",True)])

# ---- ch04
D["ch04-llm-lifecycle"] = dict(items=[
    N("pt", "Pretraining\nогромный текст,\nпредсказать токен", 0, 0, "p", 250, 110),
    N("ad", "Адаптация\nfull finetuning\nили LoRA", 320, 0, "g", 250, 110),
    N("cp", "Сжатие\ndistillation,\nquantization", 640, 0, "pu", 250, 110),
    N("in", "Inference\nAPI или свой сервер", 960, 0, "db", 250, 110),
    N("tf", "Transformer\nself-attention,\nмного параметров", 0, 220, "n", 250, 110),
    N("moe", "MoE\nработает только\nчасть экспертов", 640, 220, "n", 250, 110),
    N("cost", "Цена: обучение дорого,\nпоэтому строят\nнемногие", 320, 380, "y", 330, 110),
], edges=[E("pt","ad"),E("ad","cp"),E("cp","in"),E("tf","pt",dashed=True),E("moe","cp",dashed=True),E("cost","pt",dashed=True)])

# ---- ch05
D["ch05-brain-vs-network"] = dict(items=[
    Z("Мозг", -20, -60, 420, 560), Z("Нейросеть", 460, -60, 420, 560),
    N("b1", "Цели\nинстинкты, эмоции", 0, 20, "g", 380, 90), N("b2", "Учится всю жизнь,\nв реальном времени", 0, 140, "g", 380, 90),
    N("b3", "Память и время\nвстроены в процесс", 0, 260, "g", 380, 90), N("b4", "Смысл из опыта\nв мире", 0, 380, "g", 380, 90),
    N("a1", "Цели\nзадал человек", 480, 20, "p", 380, 90), N("a2", "Обучение отдельно,\nпотом веса заморожены", 480, 140, "p", 380, 90),
    N("a3", "Память: только\nконтекст запроса", 480, 260, "p", 380, 90), N("a4", "Слова связаны\nсо словами", 480, 380, "p", 380, 90),
], edges=[E("b1","a1",dashed=True),E("b2","a2",dashed=True),E("b3","a3",dashed=True),E("b4","a4",dashed=True)])

# ---- ch06
D["ch06-four-failures"] = dict(items=[
    N("llm", "LLM предсказывает\nследующий токен", 480, 0, "n", 300, 100),
    N("f1", "Hallucination\nуверенная ложь", 0, 200, "r", 260, 100),
    N("f2", "Чувствительность\nк prompt", 300, 200, "r", 260, 100),
    N("f3", "Jailbreak,\nprompt injection", 600, 200, "r", 260, 100),
    N("f4", "Предел\ncontext window", 900, 200, "r", 260, 100),
    N("d1", "RAG, проверка\nисточников", 0, 400, "g", 260, 100),
    N("d2", "Тесты prompt,\nevaluation", 300, 400, "g", 260, 100),
    N("d3", "Guardrails,\nменьше прав у модели", 600, 400, "g", 260, 100),
    N("d4", "Короткий контекст,\nважное в начало и конец", 900, 400, "g", 260, 100),
], edges=[E("llm","f1"),E("llm","f2"),E("llm","f3"),E("llm","f4"),E("f1","d1"),E("f2","d2"),E("f3","d3"),E("f4","d4")])

# ---- ch07
D["ch07-bias-lifecycle"] = dict(items=[
    N("dt", "Данные\nлюдские тексты\nс перекосами", 0, 0, "r", 230, 110),
    N("pr", "Pretraining\nмодель учит\nперекосы", 290, 0, "p", 230, 110),
    N("al", "Alignment\nSFT, RLHF, DPO", 580, 0, "g", 230, 110),
    N("an", "Ответ", 870, 0, "n", 200, 110),
    N("m1", "Чистка и баланс\nданных", 0, 220, "g", 230, 100),
    N("m2", "Тесты на bias,\nXAI", 290, 220, "g", 230, 100),
    N("m3", "Но модель может\nльстить (sycophancy)", 580, 220, "y", 230, 100),
    N("au", "Аудит ответов\nнаходки идут в данные\nи обучение", 870, 220, "pu", 230, 110),
], edges=[E("dt","pr"),E("pr","al"),E("al","an"),E("dt","m1",dashed=True),E("pr","m2",dashed=True),E("al","m3",dashed=True),E("an","au")])

# ---- ch08
D["ch08-ai-impact-areas"] = dict(items=[
    N("c", "LLM: язык как интерфейс", 380, 0, "p", 360, 90),
    N("w", "Работа\ncoding assistants,\nvibe coding", 0, 180, "n", 250, 110),
    N("e", "Учёба\nобъяснения\nпо запросу", 290, 180, "n", 250, 110),
    N("s", "Наука\nлитература, код,\nдокументация", 580, 180, "n", 250, 110),
    N("h", "Общение\nэмоциональная\nподдержка", 870, 180, "n", 250, 110),
    N("g1", "Быстрее прототип", 0, 340, "g", 250, 80), N("g2", "Живой тьютор", 290, 340, "g", 250, 80),
    N("g3", "Больше\nвремени на идеи", 580, 340, "g", 250, 80), N("g4", "Чувствуешь\nвнимание", 870, 340, "g", 250, 80),
    N("r1", "Код без понимания,\nбезопасность", 0, 460, "r", 250, 90), N("r2", "Cognitive debt", 290, 460, "r", 250, 90),
    N("r3", "Строгость,\nавторство", 580, 460, "r", 250, 90), N("r4", "Отношения\nодносторонние", 870, 460, "r", 250, 90),
], edges=[E("c","w"),E("c","e"),E("c","s"),E("c","h"),E("w","g1"),E("e","g2"),E("s","g3"),E("h","g4"),
          E("g1","r1"),E("g2","r2"),E("g3","r3"),E("g4","r4")])

if __name__ == "__main__":
    names = sys.argv[1:] or list(D)
    OUT.mkdir(parents=True, exist_ok=True)
    for n in names: run(n, D[n])
