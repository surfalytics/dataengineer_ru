#!/usr/bin/env python3
"""Chapter 1 (intro to AI engineering) diagrams. Usage: ch01_diagrams.py [name ...]  (no args = all)
Charts: values are read from the book's charts and rounded (see figures-ch01.md)."""
import math
from excb import N, E, Z, T, run_all

D = {}
GRAY = "#495057"


def vbars(prefix, vals, labels, x0, base, scale, bw=60, gap=20, kind="p", hl=(), lab_size=16, val_size=20, texts=None):
    """Column chart from rectangles. hl = indexes drawn red. texts = optional value labels."""
    items = []
    for i, (v, lab) in enumerate(zip(vals, labels)):
        x = x0 + i * (bw + gap)
        h = max(v * scale, 0)
        if h:
            items.append(N(f"{prefix}{i}", "", x, base - h, "r" if i in hl else kind, bw, h))
        t = texts[i] if texts else str(v)
        items.append(T(t, x + bw / 2 - val_size * 0.55 * len(t) / 2, base - h - val_size - 10, val_size, GRAY))
        items.append(T(lab, x - 2, base + 10, lab_size, GRAY))
    return items


def hbars(prefix, rows, x0, y0, scale, bh=46, step=64, label_w=330, hl=(), val_fmt=str, label_size=20):
    """Horizontal bars. rows = [(label, value, kind)]."""
    items = []
    for i, (lab, v, k) in enumerate(rows):
        y = y0 + i * step
        items.append(T(lab, x0, y + 10, label_size, GRAY))
        items.append(N(f"{prefix}{i}", "", x0 + label_w, y, "r" if i in hl else k, max(v * scale, 4), bh))
        items.append(T(val_fmt(v), x0 + label_w + v * scale + 12, y + 10, 20, GRAY))
    return items


# ---------- main diagram: chapter map ----------
D["ch01-chapter-map"] = dict(items=[
    T("От языковой модели к AI engineering", 0, -60, 24, "#1971c2"),
    N("lm", "Language model\nпредсказывает\nследующий токен", 0, 0, "p", 280, 120),
    N("llm", "LLM\nбольшая модель,\nself-supervision", 380, 0, "p", 280, 120),
    N("fm", "Foundation model\nтекст + картинки,\nобщая модель", 760, 0, "pu", 280, 120),
    N("ai", "AI engineering\nприложения на\nготовых моделях", 1140, 0, "g", 280, 120),
    N("uc", "Сценарии\nприменения\n(8 групп)", 1140, 230, "y", 280, 120),
    N("pl", "Планирование\nприложения\n(7 вопросов)", 760, 230, "y", 280, 120),
    N("st", "AI-стек:\n3 слоя и что\nизменилось", 380, 230, "q", 280, 120),
    N("cmp", "Сравнение с ML\nengineering и\nfull-stack", 0, 230, "q", 280, 120),
], edges=[E("lm", "llm"), E("llm", "fm"), E("fm", "ai"), E("ai", "uc"), E("uc", "pl"), E("pl", "st"), E("st", "cmp")])

# ---------- Fig 1-1: tokenization ----------
toks = ["I", "can", "'t", "wait", "to", "build", "awesome", "AI", "applications"]
widths = [60, 100, 80, 110, 80, 120, 160, 80, 210]
items, x = [T("Фраза: I can't wait to build awesome AI applications", 0, -10, 22, "#1971c2")], 0
for i, (t, w) in enumerate(zip(toks, widths)):
    items.append(N(f"t{i}", t, x, 60, ["p", "g", "y", "pu", "q"][i % 5], w, 70))
    x += w + 12
items += [
    T("GPT-4 режет эту фразу на 9 токенов. Слово «can't» распалось на два токена: can и 't.", 0, 170, 20, GRAY),
    T("В среднем один токен GPT-4 ≈ ¾ слова: 100 токенов ≈ 75 слов.", 0, 205, 20, "#2f9e44"),
    T("Токен может быть символом, словом или частью слова. Способ разбиения и размер словаря выбирают разработчики модели.", 0, 240, 18),
]
D["ch01-tokenization"] = dict(items=items, edges=[])

# ---------- Fig 1-2: autoregressive vs masked ----------
D["ch01-lm-types"] = dict(items=[
    T("Autoregressive LM: предсказывает токен только по токенам слева", 0, -50, 22, "#1971c2"),
    N("a_in", "The pipeline failed\nbecause the", 0, 0, "p", 330, 100),
    N("a_ctx", "Контекст:\nтолько токены слева", 440, 0, "y", 320, 100),
    N("a_pred", "[предсказание]\nsource", 870, 0, "g", 260, 100),
    T("Masked LM: заполняет пропуск по токенам слева и справа", 0, 190, 22, "#9c36b5"),
    N("m_left", "The pipeline", 0, 270, "p", 250, 80),
    N("m_pred", "[пропуск]\nfailed", 330, 260, "g", 230, 100),
    N("m_right", "because the\nsource was empty", 640, 260, "p", 330, 100),
    N("m_ctx", "Контекст:\nтокены слева и справа", 280, 460, "y", 330, 100),
], edges=[E("a_in", "a_ctx"), E("a_ctx", "a_pred"), E("m_left", "m_ctx"), E("m_right", "m_ctx"), E("m_ctx", "m_pred")])

# ---------- Fig 1-3: multimodal ----------
D["ch01-multimodal-next-token"] = dict(items=[
    T("Text tokens", 0, -40, 20, "#1971c2"),
    N("tx", "На фото\nсидит", 0, 0, "p", 230, 100),
    N("im", "Visual tokens:\nкартинка с котом", 0, 190, "q", 230, 110),
    N("md", "Multimodal\nmodel", 350, 90, "pu", 240, 110),
    T("Next token", 700, 20, 20, "#2f9e44"),
    N("out", "«кот»", 700, 60, "g", 220, 90),
    T("Модель видит токены текста и картинки вместе и выбирает следующий токен.\nГенеративная multimodal модель (LMM) может выдавать токены любой поддержанной модальности.", 0, 340, 18),
], edges=[E("tx", "md"), E("im", "md"), E("md", "out")])

# ---------- Fig 1-4: task map (bubble idea) ----------
def bub(id, text, x, y, w, h, k):
    return N(id, text, x, y, k, w, h, "ellipse")

D["ch01-task-map"] = dict(items=[
    T("Задачи benchmark Super-NaturalInstructions. Размер круга примерно показывает, сколько задач такого типа.", 0, -60, 20, "#1971c2"),
    bub("a1", "Перевод", 0, 0, 320, 210, "p"),
    bub("a2", "Вопросы\nи ответы", 350, 0, 320, 210, "q"),
    bub("a3", "Выполнение\nпрограмм", 700, 10, 270, 190, "r"),
    bub("a4", "Анализ\nтональности", 1000, 10, 270, 190, "g"),
    bub("a5", "Генерация\nвопросов", 1300, 20, 240, 170, "db"),
    bub("b1", "Сопоставление\nтекстов", 0, 240, 250, 150, "pu"),
    bub("b2", "Извлечение\nинформации", 280, 240, 250, 150, "p"),
    bub("b3", "Категоризация\nтекста", 560, 240, 250, 150, "y"),
    bub("b4", "Поиск именованных\nсущностей", 840, 240, 300, 150, "db"),
    bub("b5", "Краткое\nизложение", 1170, 240, 220, 140, "g"),
    bub("c1", "Токсичность", 0, 420, 220, 120, "r"),
    bub("c2", "Текст в код", 250, 420, 220, 120, "q"),
    bub("c3", "Перефразирование", 500, 420, 340, 120, "pu"),
    bub("c4", "Диалоги", 870, 420, 200, 110, "p"),
    bub("c5", "Математика", 1100, 420, 220, 110, "y"),
    bub("c6", "…и ещё много\nдругих", 1350, 410, 250, 130, "n"),
    T("Одна foundation model может решать все эти задачи без отдельной модели на каждую.", 0, 580, 18),
], edges=[])

# ---------- Fig 1-5: S&P 500 AI mentions ----------
q_labels = [f"Q{q}\n'{y}" for y, q in [(18, 3), (18, 4), (19, 1), (19, 2), (19, 3), (19, 4), (20, 1), (20, 2), (20, 3), (20, 4),
                                        (21, 1), (21, 2), (21, 3), (21, 4), (22, 1), (22, 2), (22, 3), (22, 4), (23, 1), (23, 2)]]
q_vals = [46, 40, 58, 50, 57, 64, 43, 53, 53, 58, 70, 60, 67, 67, 61, 58, 53, 78, 117, 177]
D["ch01-sp500-ai-mentions"] = dict(items=(
    [T("Сколько компаний из S&P 500 упомянули «AI» в отчётах о прибыли (по кварталам)", 0, -50, 22, "#1971c2")]
    + vbars("q", q_vals, q_labels, 0, 330, 1.7, bw=40, gap=16, hl=(17, 18, 19), lab_size=14, val_size=16)
    + [T("Значения подписаны на графике книги (данные FactSet). До конца 2022 года число держалось около 40–78, затем резко выросло: 177 во втором квартале 2023.", 0, 400, 18)]
), edges=[])

# ---------- Fig 1-6: GitHub stars ----------
stars = [("facebook/react", 235, "p"), ("vue.js/vue", 215, "p"), ("AutoGPT", 175, "q"), ("stable-diffusion-webui", 145, "q"),
         ("LangChain", 100, "q"), ("Ollama", 97, "q"), ("bitcoin/bitcoin", 85, "n")]
D["ch01-github-stars"] = dict(items=(
    [T("Звёзды на GitHub, тысячи (значения прочитаны с графика книги, примерно, конец 2024)", 0, -60, 22, "#1971c2")]
    + hbars("s", stars, 0, 0, 3.2, label_w=330, val_fmt=lambda v: f"{v}K")
    + [N("l1", "AI-инструменты: набрали это за 1–2 года", 0, 480, "q", 480, 60),
       N("l2", "Веб-фреймворки и bitcoin: копили с 2010–2014", 520, 480, "p", 520, 60),
       T("Оранжевые: AutoGPT, stable-diffusion-webui, LangChain, Ollama. Они уже обогнали bitcoin.", 0, 560, 18)]
), edges=[])

# ---------- Fig 1-7: use case share ----------
shares = [("Coding", 30.4, "g"), ("Conversational bots", 26.5, "p"), ("Image и video", 12.7, "p"), ("Info aggregation", 12.7, "p"),
          ("Workflow automation", 11.3, "p"), ("Writing", 3.4, "n"), ("Education", 1.5, "n"), ("Data organization", 1.5, "n")]
D["ch01-use-case-share"] = dict(items=(
    [T("Доля групп сценариев среди 205 open-source AI-приложений, %", 0, -60, 22, "#1971c2")]
    + hbars("u", shares, 0, 0, 20, label_w=330, val_fmt=lambda v: f"{v}%".replace(".", ","))
    + [T("Education, Writing и Data organization малы не потому, что непопулярны. Их чаще делают как корпоративные продукты, а не open source.", 0, 540, 18)]
), edges=[])

# ---------- Fig 1-8: enterprise willingness ----------
ent_vals = [62, 60, 59, 53, 53, 45, 39, 39]
ent_labels = ["Суммаризация\nтекста", "Управление\nзнаниями", "Поддержка\nклиентов", "Маркетинг-\nтексты", "Разработка\nПО", "Проверка\nдоговоров", "Внешний\nчат-бот", "Рекомен-\nдации"]
ent = [Z("Внутренние сценарии", -20, -90, 280, 520), Z("Внешние сценарии", 880, -90, 280, 520)]
ent += vbars("e", ent_vals, ent_labels, 0, 330, 4.6, bw=90, gap=60, kind="p", hl=(6, 7))
ent.append(T("Доля компаний, которые уже вывели сценарий в production, среди тех, кто его пробует (%)", 0, -130, 22, "#1971c2"))
ent.append(T("Внутренние сценарии выходят в production чаще. Внешние чаще останавливаются на пробах: риск выше.", 0, 450, 18))
D["ch01-enterprise-willingness"] = dict(items=ent, edges=[])

# ---------- Fig 1-9: coding time saved ----------
cod = [("Документация\nкода", 47.5, "45–50%"), ("Генерация\nкода", 40, "35–45%"), ("Рефакторинг\nкода", 25, "20–30%"), ("Очень сложные\nзадачи", 5, "до 10%")]
items = [T("На сколько AI сокращает время задачи у разработчика (данные McKinsey, из графика книги)", 0, -60, 22, "#1971c2")]
for i, (lab, v, t) in enumerate(cod):
    x = i * 230
    items.append(N(f"c{i}", "", x, 320 - v * 6, "r" if i == 3 else "p", 180, v * 6))
    items.append(T(t, x + 30, 320 - v * 6 - 36, 22, GRAY))
    items.append(T(lab, x + 10, 335, 18, GRAY))
items.append(T("Чем сложнее задача, тем меньше выигрыш. Высота столбца — середина диапазона.", 0, 400, 18))
D["ch01-coding-time-saved"] = dict(items=items, edges=[])

# ---------- Fig 1-10: Duolingo stages ----------
stages = ["1. Учебный план", "2. Исходные материалы", "3. Упражнения", "4. Персонализация урока"]
hum = [300, 195, 117, 21]
ai = [21, 117, 195, 300]
items = [T("Доля работы человека", 60, -50, 20, "#2f9e44"), T("Доля работы AI", 1000, -50, 20, "#9c36b5")]
for i, s in enumerate(stages):
    y = i * 100
    items.append(N(f"s{i}", s, 420, y, "n", 540, 80))
    items.append(N(f"h{i}", "", 400 - hum[i], y + 10, "g", hum[i], 60))
    items.append(N(f"a{i}", "", 980, y + 10, "pu", ai[i], 60))
items.append(T("Четыре этапа создания курса в Duolingo. Человек больше всего нужен в начале, AI больше всего помогает в персонализации.", 0, 420, 18))
D["ch01-duolingo-stages"] = dict(items=items, edges=[])

# ---------- Fig 1-11: MMLU vs cost (scatter, log scale) ----------
X0, BASE, DEC = 0, 440, 146.7


def px(acc):
    return X0 + (acc - 25) * 14


def py(cost):
    return BASE - (math.log10(cost) + 1) * DEC


pts = [  # name, acc, cost, kind, label dx
    ("GPT-3 Curie", 26, 6, "n", 18), ("GPT-3 Davinci", 44, 20, "n", 18), ("GPT-3.5 instruct", 65, 20, "n", -75),
    ("Llama 2 7B", 45, 0.2, "q", 18), ("Mistral 7B", 62.5, 0.25, "q", -120), ("Mixtral 8x7B", 70.5, 0.7, "q", -140),
    ("GPT-3.5 Turbo", 70, 1.7, "q", -150), ("Claude 2", 78.5, 16, "q", -100), ("GPT-4", 86.5, 45, "q", -90),
    ("Claude 3 Haiku", 75, 0.75, "pu", 18), ("Claude 3 Sonnet", 79, 9, "pu", -100), ("Claude 3 Opus", 87, 45, "pu", -30),
]
items = [T("Качество (MMLU) и цена за 1 млн токенов, 2022–2024. Шкала цены логарифмическая. Значения прочитаны с графика книги.", 0, -80, 20, "#1971c2")]
for c, lab in [(0.1, "$0.1"), (1, "$1"), (10, "$10"), (100, "$100")]:
    items.append(N(f"g{c}", "", 0, py(c), "n", 1000, 2))
    items.append(T(lab, -70, py(c) - 12, 20, GRAY))
for a in (30, 50, 70, 90):
    items.append(T(f"{a}%", px(a) - 14, BASE + 40, 18, GRAY))
items.append(T("Точность на MMLU", 380, BASE + 75, 18, GRAY))
for i, (name, acc, cost, k, dx) in enumerate(pts):
    items.append(N(f"p{i}", "", px(acc) - 9, py(cost) - 9, k, 18, 18, "ellipse"))
    ly = py(cost) - 11 + {"Claude 3 Opus": 28, "GPT-3.5 instruct": 24, "Claude 3 Sonnet": 24}.get(name, 0)
    items.append(T(name, px(acc) + dx, ly, 16, "#9c36b5" if k == "pu" else ("#e8590c" if k == "q" else GRAY)))
items += [N("y22", "2022", 1060, 0, "n", 120, 44), N("y23", "2023", 1060, 54, "q", 120, 44), N("y24", "2024", 1060, 108, "pu", 120, 44)]
D["ch01-mmlu-cost"] = dict(items=items, edges=[])

# ---------- Fig 1-12/1-13: job titles ----------
D["ch01-job-titles"] = dict(items=[
    Z("Модель A: AI engineering внутри ML engineering", -20, -70, 640, 400),
    N("a1", "ML engineer\n(Generative AI)", 20, 0, "p", 260, 90),
    N("a2", "ML engineer, LLM\nи Generative AI", 320, 0, "p", 260, 90),
    N("a3", "ML research engineer,\nfoundation models", 20, 130, "p", 260, 90),
    N("a4", "ML/AI operations\nengineer", 320, 130, "p", 260, 90),
    T("Команда ML ведёт и новую работу", 20, 255, 18),
    Z("Модель B: отдельная роль AI engineer", 700, -70, 640, 400),
    N("b1", "AI engineer", 740, 0, "g", 260, 90),
    N("b2", "Generative AI\nengineer", 1040, 0, "g", 260, 90),
    N("b3", "Lead AI engineer", 740, 130, "g", 260, 90),
    N("b4", "Senior AI research\nengineer", 1040, 130, "g", 260, 90),
    T("Для AI-приложений нанимают отдельно", 740, 255, 18),
    N("sum", "В обоих случаях задачи сильно пересекаются. ML engineer может расширить навыки до AI engineering.\nAI engineer может прийти и без опыта в ML.", 100, 400, "y", 1140, 100),
], edges=[])

# ---------- Fig 1-14: three layers ----------
def chips(prefix, y, names, k):
    return [N(f"{prefix}{i}", n, 400 + i * 230, y, k, 200, 100) for i, n in enumerate(names)]

D["ch01-ai-engineering-stack"] = dict(items=[
    N("L1", "Application\ndevelopment\n(разработка приложения)", 0, 0, "q", 340, 120),
    *chips("c1", 10, ["AI interface", "Prompt\nengineering", "Context\nconstruction", "Evaluation"], "p"),
    N("L2", "Model\ndevelopment\n(разработка модели)", 0, 190, "pu", 340, 120),
    *chips("c2", 200, ["Inference\noptimization", "Dataset\nengineering", "Modeling\n& training", "Evaluation"], "p"),
    N("L3", "Infrastructure\n(инфраструктура)", 0, 380, "db", 340, 120),
    *chips("c3", 390, ["Compute\nmanagement", "Data\nmanagement", "Serving", "Monitoring"], "p"),
    T("Приложение обычно начинают с верхнего слоя и спускаются вниз по мере нужды. Evaluation нужна в двух верхних слоях.", 0, 540, 18),
], edges=[E("L1", "L2"), E("L2", "L3")])

# ---------- Fig 1-15: repos by layer (stacked columns) ----------
cats = [("Infrastructure", "db"), ("Model development", "q"), ("Model repo", "g"), ("Application development", "r"), ("Applications", "pu")]
cols = {"2020": [15, 40, 15, 15, 5], "2022": [25, 90, 20, 20, 15], "2023": [35, 110, 65, 25, 50], "2024": [65, 215, 175, 195, 195]}
SC, BASE2 = 0.5, 460
items = [T("Накопленное число AI-репозиториев на GitHub (≥500 звёзд) по слоям. Значения прочитаны с графика книги, примерно.", 0, -40, 20, "#1971c2")]
for ci, (year, vals) in enumerate(cols.items()):
    x, ytop = ci * 190, BASE2
    for si, v in enumerate(vals):
        h = v * SC
        ytop -= h
        items.append(N(f"r{ci}{si}", str(v) if h >= 26 else "", x, ytop, cats[si][1], 140, h))
    items.append(T(f"всего ~{sum(vals)}", x + 10, ytop - 34, 18, GRAY))
    items.append(T(year, x + 45, BASE2 + 12, 20, GRAY))
leg = [("Applications (продукты верхнего слоя)", "pu"), ("Application development", "r"), ("Model repo (продукты слоя модели)", "g"),
       ("Model development", "q"), ("Infrastructure", "db")]
for i, (t, k) in enumerate(leg):
    items.append(N(f"lg{i}", t, 820, i * 70, k, 440, 56))
items.append(T("Вехи: TensorFlow (2015), статья про Transformers (2017), библиотека Hugging Face Transformers (2018),\nGPT-3 (2020), Stable Diffusion (авг. 2022), ChatGPT (ноя. 2022).", 0, 510, 18))
items.append(T("Infrastructure растёт медленнее всех: требования к ресурсам, deployment и мониторингу почти не изменились.", 0, 580, 18, "#2f9e44"))
D["ch01-repos-by-layer"] = dict(items=items, edges=[])

# ---------- Fig 1-16: workflow order ----------
D["ch01-workflow-order"] = dict(items=[
    N("l1", "ML engineering", 0, 0, "n", 250, 90),
    N("m1", "Data\nсобрать данные", 330, 0, "db", 250, 90),
    N("m2", "Model\nобучить модель", 680, 0, "pu", 250, 90),
    N("m3", "Product\nсделать продукт", 1030, 0, "g", 250, 90),
    N("l2", "AI engineering", 0, 190, "n", 250, 90),
    N("n1", "Product\nсделать продукт", 330, 190, "g", 250, 90),
    N("n2", "Data\nсобрать данные", 680, 190, "db", 250, 90),
    N("n3", "Model\nдообучить модель", 1030, 190, "pu", 250, 90),
    T("С готовыми моделями продукт можно сделать первым. Данные и свою модель вкладывают, когда продукт уже показал пользу.", 0, 330, 18),
], edges=[E("m1", "m2"), E("m2", "m3"), E("n1", "n2"), E("n2", "n3")])

# ---------- own: self-supervision ----------
D["ch01-self-supervision"] = dict(items=[
    T("Supervised: метки ставят люди", 0, -50, 22, "#e03131"),
    N("s1", "Транзакции\nбез меток", 0, 0, "n", 240, 100),
    N("s2", "Люди ставят метки:\n«фрод» / «не фрод»\n(дорого и медленно)", 330, 0, "r", 340, 110),
    N("s3", "Размеченные\nданные", 760, 0, "p", 240, 100),
    N("s4", "Модель", 1090, 0, "pu", 200, 100),
    T("Self-supervised: метки берутся из самих данных", 0, 190, 22, "#2f9e44"),
    N("t1", "Текст из книг,\nблогов, статей", 0, 250, "n", 240, 100),
    N("t2", "Метка уже есть:\nследующий токен\nв самом тексте", 330, 240, "g", 340, 120),
    N("t3", "Миллиарды примеров\n«контекст → токен»", 760, 250, "p", 280, 100),
    N("t4", "Модель", 1130, 250, "pu", 200, 100),
    T("Self-supervised не то же самое, что unsupervised: там меток нет совсем, а здесь метки выводят из входа.", 0, 400, 18),
], edges=[E("s1", "s2"), E("s2", "s3"), E("s3", "s4"), E("t1", "t2"), E("t2", "t3"), E("t3", "t4")])

# ---------- own: adaptation techniques ----------
D["ch01-adaptation-techniques"] = dict(items=[
    Z("Веса модели не меняются", -20, -70, 700, 520),
    Z("Веса меняются", 720, -70, 380, 520),
    N("p1", "Prompt engineering", 0, 0, "p", 300, 80),
    N("p2", "RAG", 360, 0, "p", 300, 80),
    N("p3", "Finetuning", 740, 0, "pu", 340, 80),
    N("e1", "Инструкции и примеры\nнужных описаний товара", 0, 130, "n", 300, 100),
    N("e2", "База отзывов клиентов\nпомогает писать точнее", 360, 130, "n", 300, 100),
    N("e3", "Дообучение на датасете\nхороших описаний", 740, 130, "n", 340, 100),
    N("n1", "Нужно мало данных.\nПроще всего начать.\nСложным задачам\nможет не хватить.", 0, 290, "y", 300, 130),
    N("n2", "Нужна база знаний\nи поиск по ней.\nМодель получает контекст.", 360, 290, "y", 300, 120),
    N("n3", "Нужно больше данных\nи сложнее. Улучшает\nкачество, latency, цену.", 740, 290, "y", 340, 120),
], edges=[E("p1", "e1", dashed=True), E("p2", "e2", dashed=True), E("p3", "e3", dashed=True),
          E("e1", "n1", dashed=True), E("e2", "n2", dashed=True), E("e3", "n3", dashed=True)])

# ---------- own: product dimensions ----------
D["ch01-product-dimensions"] = dict(items=[
    N("a1", "Критичная функция\nFace ID: без AI не работает", 0, 0, "r", 340, 100),
    N("a2", "Дополнение\nSmart Compose в Gmail", 480, 0, "g", 340, 100),
    N("an", "Чем критичнее AI, тем выше\nтребования к точности.\nОшибки в дополнении прощают.", 960, -5, "y", 400, 110),
    N("b1", "Реактивная функция\nчат-бот: ждёт вопроса", 0, 170, "p", 340, 100),
    N("b2", "Проактивная функция\nпредупреждение о пробке", 480, 170, "pu", 340, 100),
    N("bn", "Проактивную не просили,\nпоэтому качество выше.\nЗадержка менее важна.", 960, 165, "y", 400, 110),
    N("c1", "Динамическая функция\nобновляется по отзывам,\nпамять ChatGPT", 0, 340, "p", 340, 110),
    N("c2", "Статическая функция\nобновляется с релизом\n(поиск объектов на фото)", 480, 340, "n", 340, 110),
    N("cn", "Динамической может быть\nмодель на пользователя\nили память о нём.", 960, 335, "y", 400, 110),
], edges=[E("a1", "a2", head=False), E("a2", "an", dashed=True, head=False), E("b1", "b2", head=False), E("b2", "bn", dashed=True, head=False),
          E("c1", "c2", head=False), E("c2", "cn", dashed=True, head=False)])

# ---------- own: crawl-walk-run ----------
D["ch01-crawl-walk-run"] = dict(items=[
    N("c", "Crawl\nчеловек обязателен", 0, 0, "y", 330, 100),
    N("w", "Walk\nAI общается с\nсотрудниками компании", 450, -5, "p", 340, 110),
    N("r", "Run\nбольше автоматизации,\nAI общается с клиентами", 910, -5, "g", 400, 110),
    N("ec", "Бот поддержки подсказывает\nответы операторам", 0, 210, "n", 330, 100),
    N("ew", "Операторы принимают ≥95%\nподсказок без правок\nна простых вопросах", 450, 205, "n", 340, 110),
    N("er", "На простые вопросы бот\nотвечает клиентам сам", 910, 210, "n", 400, 100),
    T("Роль человека меняется вместе с качеством системы. Переход решают метрики, а не интуиция.", 0, 360, 18),
], edges=[E("c", "w"), E("w", "r"), E("c", "ec", dashed=True), E("w", "ew", dashed=True), E("r", "er", dashed=True)])

# ---------- own: last mile ----------
D["ch01-last-mile"] = dict(items=[
    T("Пример LinkedIn: время до качества продукта (по рассказу книги)", 0, -60, 22, "#1971c2"),
    N("b1", "месяц 1", 0, 0, "g", 150, 70),
    T("0 → 80% желаемого опыта. Быстро.", 190, 20, 20, "#2f9e44"),
    N("b2", "ещё 4 месяца", 0, 110, "r", 600, 70),
    T("80 → 95%. Борьба с галлюцинациями и мелочами. Каждый процент стоит очень дорого.", 640, 125, 18, "#e03131"),
    N("n", "На 1 процентный пункт во втором отрезке ушло примерно в 21 раз больше времени, чем в первом (4 месяца на 15 п.п. против 1 месяца на 80 п.п.).", 0, 230, "y", 1300, 90),
    T("«От 0 до 60 идти легко, от 60 до 100 трудно» — пишут авторы UltraChat.", 0, 345, 18),
], edges=[])

# ---------- own: training terms ----------
D["ch01-training-terms"] = dict(items=[
    Z("Training = любое обучение, которое меняет веса", -20, -70, 1420, 330),
    N("pre", "Pre-training\nвеса случайные,\nобучение с нуля", 0, 0, "r", 300, 130),
    N("post", "Post-training\nдообучение у разработчика\nмодели (лучше слушать\nинструкции)", 460, -10, "p", 380, 150),
    N("ft", "Finetuning\nдообучение у разработчика\nприложения (под вашу\nзадачу)", 960, -10, "g", 400, 150),
    T("Самый дорогой этап: у InstructGPT до 98% ресурсов", 0, 150, 16, "#e03131"),
    T("Pre-training и post-training образуют спектр: процессы и инструменты похожи.", 460, 190, 16),
    N("pe", "Prompt engineering\nвеса не меняются,\nэто не training", 0, 330, "y", 330, 110),
    N("qt", "Quantization\nвеса меняются (точность\nснижается), но это\nне training", 460, 330, "y", 420, 110),
], edges=[E("pre", "post"), E("post", "ft")])

# ---------- own: moats ----------
D["ch01-moats"] = dict(items=[
    N("t", "Технология\nядро у всех похоже:\nмодели общие", 0, 0, "r", 340, 120),
    N("d", "Дистрибуция\nбольшие компании\nуже у пользователей", 450, 0, "r", 340, 120),
    N("da", "Данные\nкто первым собрал данные\nоб использовании, тот\nулучшает продукт быстрее", 900, -10, "g", 420, 140),
    N("tv", "Защиты почти нет", 0, 200, "n", 340, 70),
    N("dv", "Преимущество у больших", 450, 200, "n", 340, 70),
    N("dav", "Шанс стартапа", 900, 200, "n", 420, 70),
    T("Если продукт — функция чужой платформы, платформа может повторить его за пару недель.", 0, 320, 18),
], edges=[E("t", "tv", dashed=True), E("d", "dv", dashed=True), E("da", "dav", dashed=True)])

# ---------- own: planning path ----------
D["ch01-planning-path"] = dict(items=[
    N("p1", "1. Зачем?\nОценка сценария\nи риска", 0, 0, "p", 290, 110),
    N("p2", "2. Строить\nили покупать?", 360, 0, "p", 290, 110),
    N("p3", "3. Роль AI\nи человека", 720, 0, "p", 290, 110),
    N("p4", "4. Защита\nпродукта", 1080, 0, "p", 290, 110),
    N("p5", "5. Метрики и\nпорог полезности", 1080, 220, "y", 290, 110),
    N("p6", "6. Этапы\nи last mile", 720, 220, "y", 290, 110),
    N("p7", "7. Поддержка:\nмодели и цены\nменяются", 360, 220, "y", 290, 110),
], edges=[E("p1", "p2"), E("p2", "p3"), E("p3", "p4"), E("p4", "p5"), E("p5", "p6"), E("p6", "p7")])

if __name__ == "__main__":
    run_all(D)
