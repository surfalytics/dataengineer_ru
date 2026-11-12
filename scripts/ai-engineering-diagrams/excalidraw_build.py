#!/usr/bin/env python3
"""Build the non-ER book diagrams in Excalidraw (needs the local canvas server on :3456).
Each diagram is a small spec (nodes at x/y, edges). Output: public/assets/ai-engineering/<name>.png
Scenes are saved as dataengineer_ru/aie-<name> in ~/dev/excalidraw/diagrams.
Usage: excalidraw_build.py [name ...]   (no args = all)"""
import base64, json, subprocess, sys, urllib.error, urllib.request
from pathlib import Path

API = "http://127.0.0.1:3456"
OUT = Path(__file__).resolve().parents[2] / "public/assets/ai-engineering"
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
    scene = f"dataengineer_ru/aie-{name}"
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


D = {}

# ---- ch00 book map
D["ch00-book-map"] = dict(items=[
    Z("Основы", -20, -60, 320, 360), Z("Оценка", 360, -60, 320, 360),
    Z("Адаптация модели", 740, -60, 320, 700), Z("Продакшен", 1120, -60, 320, 360),
    N("c1", "1. Введение в\nAI engineering", 0, 20, "p", 280), N("c2", "2. Foundation\nmodels", 0, 160, "p", 280),
    N("c3", "3. Методология\nоценки", 380, 20, "y", 280), N("c4", "4. Оценка\nAI-систем", 380, 160, "y", 280),
    N("c5", "5. Prompt\nengineering", 760, 20, "g", 280), N("c6", "6. RAG\nи агенты", 760, 160, "g", 280),
    N("c7", "7. Finetuning", 760, 300, "g", 280), N("c8", "8. Dataset\nengineering", 760, 440, "g", 280),
    N("c9", "9. Оптимизация\ninference", 1140, 20, "pu", 280), N("c10", "10. Архитектура\nи feedback", 1140, 160, "pu", 280),
], edges=[E("c1","c3"),E("c3","c5"),E("c5","c9")])

# ---- ch01
D["ch01-ai-engineering-stack"] = dict(items=[
    N("app", "Application development\nprompt, context (RAG),\nevaluation, интерфейс", 0, 0, "p", 480, 130),
    N("mod", "Model development\nfinetuning, datasets,\ninference optimization", 0, 180, "pu", 480, 130),
    N("inf", "Infrastructure\nserving, compute,\nмониторинг", 0, 360, "n", 480, 130),
    N("note", "Главный вес сегодня\nв верхнем слое:\nprompt, данные, оценка.\nМодель берут готовую.", 580, 0, "y", 320, 160),
    N("ml", "Классический ML:\nсначала своя модель,\nпотом приложение", 580, 330, "n", 320, 140),
], edges=[E("app","mod"),E("mod","inf"),E("note","app",dashed=True)])

# ---- ch02
D["ch02-model-training-stages"] = dict(items=[
    N("raw", "Сырой текст\nинтернет, книги, код", 0, 0, "n", 260, 110),
    N("pre", "Pre-training\nпредсказать\nследующий токен", 320, 0, "p", 260, 110),
    N("sft", "Supervised\nfinetuning\nинструкция → ответ", 640, 0, "g", 260, 110),
    N("pref", "Preference\nfinetuning (RLHF)\nлюди выбирают ответ", 960, 0, "pu", 260, 110),
    N("pre1", "Знает язык и факты,\nно только продолжает\nтекст", 320, 220, "y", 260, 110),
    N("sft1", "Следует инструкциям,\nотвечает как\nпомощник", 640, 220, "y", 260, 110),
    N("pref1", "Ответы полезнее\nи безопаснее,\nнужный тон", 960, 220, "y", 260, 110),
], edges=[E("raw","pre"),E("pre","sft"),E("sft","pref"),E("pre","pre1",dashed=True),E("sft","sft1",dashed=True),E("pref","pref1",dashed=True)])

D["ch02-sampling"] = dict(items=[
    N("m", "Модель\nлогиты для всех\nтокенов", 0, 0, "p", 260, 110),
    N("t", "Temperature\nвыше: случайнее\nниже: стабильнее", 320, 0, "y", 260, 110),
    N("k", "Top-k / Top-p\nоставить только\nлучших кандидатов", 640, 0, "pu", 260, 110),
    N("s", "Sampling\nвыбор токена\nпо вероятности", 960, 0, "g", 260, 110),
    T("temperature 0 = почти всегда самый вероятный токен", 0, 170, 20, "#495057"),
    T("Structured output (JSON): допустимы только токены, которые подходят по формату", 0, 210, 20, "#495057"),
    T("Выбранный токен добавляется к тексту. Цикл идёт, пока не будет конец ответа.", 0, 250, 20, "#495057"),
], edges=[E("m","t"),E("t","k"),E("k","s")])

# ---- ch03
D["ch03-evaluation-methods"] = dict(items=[
    N("root", "Evaluation\nметоды оценки", 620, 0, "n", 260, 100),
    N("ex", "Exact evaluation\nесть правильный ответ", 270, 170, "p", 280, 100),
    N("sub", "Subjective evaluation\nнет одного ответа", 975, 170, "y", 280, 100),
    N("f1", "Functional\ncorrectness\nкод проходит тесты", 0, 340, "g", 250, 120),
    N("f2", "Сравнение с эталоном\nexact match,\nlexical", 270, 340, "p", 250, 120),
    N("f3", "Semantic\nsimilarity\nembeddings", 540, 340, "p", 250, 120),
    N("j1", "AI as a judge\nмодель ставит\nоценку", 840, 340, "pu", 250, 120),
    N("j2", "Comparative\nпопарные сравнения,\nранг моделей", 1110, 340, "pu", 250, 120),
    N("w1", "SQL, код,\nклассификация", 0, 540, "n", 250, 100),
    N("w2", "Перевод, summary\nс эталоном", 270, 540, "n", 250, 100),
    N("w3", "Смысл важнее\nточных слов", 540, 540, "n", 250, 100),
    N("w4", "Открытые ответы,\nдёшево и быстро", 840, 540, "n", 250, 100),
    N("w5", "Предпочтения людей,\nrating", 1110, 540, "n", 250, 100),
    T("↑ Когда использовать", 0, 665, 20, "#495057"),
], edges=[E("root","ex"),E("root","sub"),E("ex","f1"),E("ex","f2"),E("ex","f3"),E("sub","j1"),E("sub","j2"),
          E("f1","w1",dashed=True),E("f2","w2",dashed=True),E("f3","w3",dashed=True),E("j1","w4",dashed=True),E("j2","w5",dashed=True)])

# ---- ch04
D["ch04-evaluation-pipeline"] = dict(items=[
    N("s1", "1. Оценить все\nкомпоненты\nprompt, retrieval, модель", 0, 0, "p", 320, 120),
    N("s2", "2. Guideline оценки\nкритерии, шкала,\nсвязь с бизнес-метриками", 0, 190, "p", 320, 120),
    N("s3", "3. Методы и данные\nсрезы, разметка,\nпроверка самой оценки", 0, 380, "p", 320, 120),
    N("chg", "Изменить prompt,\nмодель или данные", 480, 190, "y", 280, 120),
    N("ok", "Метрики растут?\nВ продакшен", 480, 380, "g", 280, 120),
], edges=[E("s1","s2"),E("s2","s3"),E("s3","chg","нет"),E("chg","s1","цикл"),E("s3","ok","да")])

# ---- ch05
D["ch05-prompt-anatomy"] = dict(items=[
    N("sys", "System prompt\nроль, правила, формат", 0, 0, "p", 300, 100),
    N("task", "Задача\nчто сделать", 0, 130, "p", 300, 100),
    N("ex", "Примеры\nfew-shot", 0, 260, "g", 300, 100),
    N("ctx", "Контекст\nRAG, документы", 0, 390, "db", 300, 100),
    N("usr", "Ввод пользователя", 0, 520, "n", 300, 100),
    N("mod", "Модель", 420, 0, "pu", 200, 620),
    N("out", "Ответ", 720, 260, "g", 240, 100),
    N("note", "Промпт = код:\nверсия в git, тесты,\nметрики качества", 380, 680, "y", 320, 120),
], edges=[E("sys","mod"),E("task","mod"),E("ex","mod"),E("ctx","mod"),E("usr","mod"),E("mod","out"),E("note","mod",dashed=True)])

# ---- ch06
D["ch06-rag-pipeline"] = dict(items=[
    Z("Индексация (офлайн)", -20, -60, 1060, 240), Z("Запрос (онлайн)", -20, 260, 1320, 240),
    N("d", "Документы", 0, 0, "n", 220, 100), N("ch", "Chunking\nнарезка", 260, 0, "pu", 220, 100),
    N("em", "Embeddings", 520, 0, "pu", 220, 100), N("vs", "Vector store", 780, 0, "db", 220, 100),
    N("q", "Вопрос", 0, 340, "n", 220, 100), N("rt", "Retriever\n+ rewrite, rerank", 260, 340, "p", 220, 100),
    N("cx", "Context + prompt", 520, 340, "p", 220, 100), N("md", "Модель", 780, 340, "pu", 220, 100),
    N("an", "Ответ", 1040, 340, "g", 220, 100),
], edges=[E("d","ch"),E("ch","em"),E("em","vs"),E("q","rt"),E("rt","cx"),E("cx","md"),E("md","an"),E("vs","rt","top-k",True)])

D["ch06-agent-loop"] = dict(items=[
    N("mem", "Memory\nкороткая и\nдолгая", 300, -220, "db", 250, 110), N("tools", "Tools\nsearch, SQL,\nкод, API", 600, -220, "db", 250, 110),
    N("task", "Задача", 0, 0, "n", 250, 100), N("plan", "Plan\nразбить на шаги", 300, 0, "p", 250, 100),
    N("act", "Act\nвызвать tool", 600, 0, "pu", 250, 100), N("obs", "Observe\nрезультат tool", 900, 0, "p", 250, 100),
    N("dec", "Задача\nрешена?", 600, 260, "q", 300, 170, "diamond"), N("ans", "Ответ", 260, 295, "g", 250, 100),
], edges=[E("task","plan"),E("plan","act"),E("act","obs"),E("obs","dec"),E("dec","ans","да"),E("dec","plan","нет: reflect"),
          E("mem","plan",dashed=True,head=False),E("tools","act",dashed=True,head=False)])

# ---- ch07
D["ch07-finetune-or-not"] = dict(items=[
    N("t", "Задача", 400, 0, "n", 250, 90), N("p", "Prompt engineering\nпопробовать сначала", 400, 140, "p", 250, 100),
    N("d1", "Качества\nхватает?", 375, 290, "q", 300, 170, "diamond"), N("stop", "Остановиться", 850, 330, "g", 250, 90),
    N("d2", "Что не так:\nфакты или форма?", 350, 540, "q", 350, 180, "diamond"),
    N("rag", "RAG\nсвежие и частные\nфакты", 0, 820, "db", 280, 120), N("ft", "Finetuning\nLoRA / QLoRA\nформа, стиль, размер", 770, 820, "pu", 280, 120),
    N("note", "Finetune для формы,\nRAG для фактов", 375, 840, "y", 300, 100),
], edges=[E("t","p"),E("p","d1"),E("d1","stop","да"),E("d1","d2","нет"),E("d2","rag","факты"),E("d2","ft","форма")])

# ---- ch08
D["ch08-dataset-pipeline"] = dict(items=[
    N("src", "Источники: свои данные, открытые датасеты,\nразметка людьми, синтетика", 0, 0, "n", 1040, 100),
    N("i", "Inspect\nпосмотреть данные", 0, 200, "p", 230, 100), N("dd", "Deduplicate\nубрать дубли", 270, 200, "p", 230, 100),
    N("cl", "Clean + filter\nмусор, PII, токсичность", 540, 200, "p", 230, 100), N("fm", "Format\nпод модель", 810, 200, "p", 230, 100),
    N("ds", "Датасет для обучения\nи оценки", 360, 400, "db", 320, 110),
    N("a1", "Quality\nкачество", 0, 580, "y", 230, 100), N("a2", "Coverage\nпокрытие случаев", 400, 580, "y", 240, 100),
    N("a3", "Quantity\nколичество", 810, 580, "y", 230, 100),
], edges=[E("src","i"),E("i","dd"),E("dd","cl"),E("cl","fm"),E("fm","ds"),E("a1","ds",dashed=True),E("a2","ds",dashed=True),E("a3","ds",dashed=True)])

# ---- ch09
D["ch09-inference-phases"] = dict(items=[
    N("pr", "Промпт", 0, 0, "n", 230, 110),
    N("pf", "Prefill\nвесь промпт сразу\ncompute-bound", 300, 0, "p", 250, 110),
    N("dc", "Decode\nтокен за токеном\nmemory-bandwidth", 740, 0, "g", 250, 110),
    N("an", "Ответ", 1060, 0, "n", 200, 110),
    N("kv", "KV cache", 570, 200, "db", 150, 90),
    N("tt", "TTFT\nпервый токен", 300, 200, "y", 230, 100), N("tp", "TPOT\nтокен в ответе", 740, 200, "y", 250, 100),
    Z("Три уровня оптимизации", -20, 350, 1340, 250),
    N("o1", "Модель\nquantization, distillation,\nspeculative decoding", 10, 420, "pu", 400, 130),
    N("o2", "Attention и KV cache\nPagedAttention,\nFlashAttention", 470, 420, "pu", 380, 130),
    N("o3", "Сервис\nbatching, prompt cache,\nparallelism", 910, 420, "pu", 380, 130),
], edges=[E("pr","pf"),E("pf","dc","tokens"),E("dc","an"),E("pf","kv",dashed=True),E("kv","dc",dashed=True),
          E("pf","tt",dashed=True),E("dc","tp",dashed=True)])

# ---- ch10
D["ch10-architecture"] = dict(items=[
    Z("Monitoring и observability: logs, metrics, traces", -30, -60, 1250, 640),
    N("q", "Запрос\nпользователя", 0, 20, "n", 250, 100), N("ig", "Input guardrails\nPII, атаки", 310, 20, "y", 250, 100),
    N("rt", "Router + gateway\nвыбор модели", 620, 20, "p", 250, 100), N("cx", "Context\nRAG, tools", 930, 20, "db", 250, 100),
    N("ca", "Cache\nexact, semantic", 930, 240, "pu", 250, 100), N("md", "Модель", 620, 240, "p", 250, 100),
    N("og", "Output guardrails\nфакты, безопасность", 310, 240, "y", 250, 100), N("rs", "Ответ", 0, 240, "g", 250, 100),
    N("fb", "User feedback\nсигналы, оценки", 0, 450, "y", 250, 100),
    T("cache hit: ответ из кэша идёт сразу к output guardrails, модель не вызывается", 310, 380, 18, "#868e96"),
], edges=[E("q","ig"),E("ig","rt"),E("rt","cx"),E("cx","ca"),E("ca","md","miss"),E("md","og"),E("og","rs"),E("rs","fb")])

if __name__ == "__main__":
    names = sys.argv[1:] or list(D)
    OUT.mkdir(parents=True, exist_ok=True)
    for n in names: run(n, D[n])
