#!/usr/bin/env python3
"""Chapter 7 (finetuning) diagrams. Usage: ch07_diagrams.py [name ...]  (no args = all)"""
import math

from excb import N, E, Z, T, run_all

D = {}
GRAY = "#495057"


def fmt(v):
    """Число с десятичной запятой, как принято в русском тексте."""
    return f"{v:g}".replace(".", ",")


# ---------------------------------------------------------------- main map
D["ch07-finetuning-map"] = dict(items=[
    N("root", "Finetuning: меняем веса модели", 560, 0, "n", 420, 80),
    N("h1", "1. Стоит ли делать?\nпричины за и против;\nfinetuning или RAG", 0, 170, "y", 340, 130),
    N("h2", "2. Почему это трудно:\nпамять GPU; числовые\nформаты; quantization", 400, 170, "r", 340, 130),
    N("h3", "3. Как сделать дешевле:\nPEFT, LoRA, QLoRA;\nmodel merging", 800, 170, "g", 340, 130),
    N("h4", "4. Тактика:\nбазовая модель, метод,\nframework, hyperparameters", 1200, 170, "p", 380, 130),
    N("n1", "Форма — finetuning,\nфакты — RAG.\nСначала prompt", 0, 380, "n", 340, 120),
    N("n2", "7B, Adam, 16 бит:\n56 ГБ при обучении\nпротив 14 ГБ весов", 400, 380, "n", 340, 120),
    N("n3", "LoRA учит ~0,01%\nпараметров. QLoRA:\n65B на одной GPU 48 ГБ", 800, 380, "n", 340, 120),
    N("n4", "Начните с LoRA и сильной\nмодели; подбирайте lr,\nbatch size, epochs", 1200, 380, "n", 380, 120),
], edges=[E("root", "h1"), E("root", "h2"), E("root", "h3"), E("root", "h4"),
          E("h1", "n1", dashed=True), E("h2", "n2", dashed=True), E("h3", "n3", dashed=True), E("h4", "n4", dashed=True)])

# ---------------------------------------------------------------- 7-1 Code Llama
D["ch07-code-llama"] = dict(items=[
    N("l2", "Llama 2\nfoundation model\n7B, 13B, 34B", 0, 160, "n", 250, 120),
    N("ct", "Code training +\ninfilling (заполнение\nпропусков)\n500B токенов", 310, 150, "pu", 300, 140),
    N("lc1", "Long-context\nfinetuning\n20B токенов", 680, 0, "g", 250, 120),
    N("py", "Python code\ntraining\n100B токенов", 680, 320, "p", 250, 120),
    N("lc2", "Long-context\nfinetuning\n20B токенов", 990, 320, "g", 250, 120),
    N("ift", "Instruction\nfinetuning (SFT)\n5B токенов", 990, 160, "y", 250, 120),
    N("o1", "Code Llama\n7B, 13B, 34B", 1300, 0, "g", 300, 100),
    N("o2", "Code Llama-Instruct\n7B, 13B, 34B", 1300, 170, "g", 300, 100),
    N("o3", "Code Llama-Python\n7B, 13B, 34B", 1300, 330, "g", 300, 100),
    T("Каждый шаг — отдельный вид finetuning поверх предыдущего. Числа: сколько токенов данных на шаге.", 0, 480, 18),
], edges=[E("l2", "ct"), E("ct", "lc1"), E("ct", "py"), E("lc1", "o1"), E("lc1", "ift"), E("ift", "o2"),
          E("py", "lc2"), E("lc2", "o3")])

# ---------------------------------------------------------------- 7-2 prompt vs finetune
D["ch07-prompt-vs-finetune"] = dict(items=[
    Z("Prompt: примеры едут в каждом запросе", -20, -60, 1260, 260),
    N("p1", "Prompt:\nинструкция + примеры\n+ новый вход", 0, 20, "y", 300, 130),
    N("p2", "Предобученная\nмодель", 420, 35, "p", 260, 100),
    N("p3", "Ответ", 800, 35, "g", 200, 100),
    T("Больше примеров = больше токенов = выше стоимость и latency", 0, 165, 18, "#e03131"),
    Z("Finetuning: примеры уходят в веса один раз", -20, 250, 1260, 520),
    N("f1", "Предобученная\nмодель", 420, 320, "p", 260, 100),
    N("f2", "Finetuning\n(обучение)", 420, 490, "pu", 260, 100, "diamond"),
    N("f3", "Примеры\n(инструкция, ответ)", 0, 490, "n", 300, 100),
    N("f4", "Дообученная\nмодель", 420, 650, "g", 260, 100),
    N("f5", "Короткий prompt:\nтолько новый вход", 0, 650, "y", 300, 100),
    N("f6", "Ответ", 800, 650, "g", 200, 100),
], edges=[E("p1", "p2"), E("p2", "p3"), E("f1", "f2"), E("f3", "f2"), E("f2", "f4"), E("f5", "f4"), E("f4", "f6")])

# ---------------------------------------------------------------- 7-3 adaptation path
D["ch07-adaptation-path"] = dict(items=[
    Z("Prompt и RAG: оптимизация контекста", -30, -70, 480, 700),
    Z("Finetuning: оптимизация поведения", 560, -70, 520, 700),
    N("a1", "1. Prompt\n(системно, с eval)", 0, 0, "y", 400, 90),
    N("a2", "2. Добавить примеры\nв prompt (1–50)", 0, 150, "y", 400, 90),
    N("a3", "3. Простой retrieval\n(BM25)", 0, 300, "g", 400, 90),
    N("a4", "4. Сложный retrieval\n(embeddings, hybrid)", 0, 470, "g", 400, 90),
    N("b1", "Finetuning\n(LoRA и другие)", 620, 300, "pu", 400, 90),
    N("b2", "RAG + дообученная\nмодель", 620, 470, "p", 400, 90),
    T("Время идёт сверху вниз. Следующий шаг выбирает тип ошибок.", 0, 650, 18),
], edges=[E("a1", "a2"), E("a2", "a3"), E("a3", "a4", "ещё ошибки фактов"), E("a3", "b1", "ошибки формы"),
          E("a4", "b2"), E("b1", "b2")])

# ---------------------------------------------------------------- finetune or not (our decision tree)
D["ch07-finetune-or-not"] = dict(items=[
    N("s", "Модель не справляется\nс задачей", 520, 0, "n", 300, 90),
    N("q1", "Есть eval и\nсистемный prompt?", 490, 150, "y", 360, 150, "diamond"),
    N("no", "Сначала eval и prompt\n(главы 4 и 5),\nпотом вернитесь сюда", 0, 165, "r", 340, 120),
    N("q2", "Какие ошибки?", 520, 400, "y", 300, 120, "diamond"),
    N("i", "Информационные:\nнет или устарели факты", 0, 600, "g", 340, 100),
    N("rag", "RAG: сначала BM25,\nпотом embeddings", 0, 760, "g", 340, 100),
    N("b", "Поведенческие:\nформа, стиль, формат", 1000, 600, "p", 340, 100),
    N("ft", "Finetuning:\nсначала LoRA", 1000, 760, "p", 340, 100),
    N("both", "Оба типа:\nначните с RAG", 520, 600, "q", 300, 100),
    N("comb", "Затем finetuning,\nпотом RAG + finetuned model", 480, 760, "pu", 380, 100),
], edges=[E("s", "q1"), E("q1", "no", "нет"), E("q1", "q2", "да"), E("q2", "i"), E("q2", "both"), E("q2", "b"),
          E("i", "rag"), E("b", "ft"), E("both", "comb")])

# ---------------------------------------------------------------- 7-4 forward / backward
D["ch07-forward-backward"] = dict(items=[
    Z("Forward pass: считаем ответ", -20, -60, 1780, 210),
    N("in", "Вход", 0, 0, "n", 170, 80),
    N("w", "Параметр w\n(вес)", 260, 0, "p", 200, 80),
    N("f", "Функция\nактивации f", 550, 0, "p", 210, 80),
    N("a", "Activation a\n(промежуточное\nзначение)", 850, -10, "p", 230, 100),
    N("out", "Ответ модели", 1170, 0, "p", 210, 80),
    N("loss", "Loss: разница с\nожидаемым ответом", 1450, -10, "r", 270, 100),
    Z("Backward pass: считаем gradients и меняем веса", -20, 220, 1780, 330),
    N("da", "Gradient для a\n(вклад a в ошибку)", 790, 290, "y", 290, 100),
    N("dw", "Gradient для w\n(вклад w в ошибку)", 260, 290, "y", 290, 100),
    N("opt", "Optimizer (SGD, Adam)\nменяет w по gradient", 0, 450, "pu", 330, 80),
], edges=[E("in", "w"), E("w", "f"), E("f", "a"), E("a", "out"), E("out", "loss"),
          E("loss", "da", "обратный путь", dashed=True), E("da", "dw", dashed=True), E("dw", "opt", dashed=True)])

# ---------------------------------------------------------------- 7-5 activation memory (stacked bars)


def stacked_activation_chart():
    base, scale, bw = 520, 3.2, 80
    groups = [("22B", (46, 59), (46, 10)), ("175B", (46, 66), (46, 12)),
              ("530B", (31, 114), (31, 24)), ("1T", (32, 132), (32, 27))]
    items = [T("Память при обучении, ГБ (значения прочитаны с графика книги и округлены)", 0, -75, 22, "#1971c2"),
             N("lim", "", -10, base - 80 * scale - 2, "r", 1290, 4),
             T("80 ГБ:\nмощная GPU", 1100, base - 80 * scale - 56, 18, "#e03131")]
    for gi, (name, bad, good) in enumerate(groups):
        x0 = gi * 290
        for bi, (vals, label) in enumerate([(bad, "без\nпересчёта"), (good, "с пересчётом\nactivations")]):
            x = x0 + bi * (bw + 30)
            hp, ha = vals[0] * scale, vals[1] * scale
            items.append(N(f"p{gi}{bi}", "", x, base - hp, "p", bw, hp))
            items.append(N(f"a{gi}{bi}", "", x, base - hp - ha, "g", bw, ha))
            total = vals[0] + vals[1]
            items.append(T(str(total), x + bw / 2 - 12, base - hp - ha - 30, 20, GRAY))
            items.append(T(label, x - 12, base + 8, 14, GRAY))
        items.append(T(name, x0 + 62, base + 62, 22, GRAY))
    items += [N("lg1", "", 0, base + 110, "p", 24, 24), T("параметры и optimizer states", 34, base + 108, 18, GRAY),
              N("lg2", "", 380, base + 110, "g", 24, 24), T("activations", 414, base + 108, 18, GRAY)]
    return dict(items=items, edges=[])


D["ch07-activation-memory"] = stacked_activation_chart()

# ---------------------------------------------------------------- 7-6 number formats


def number_formats():
    u = 17  # px на бит
    rows = [("FP32", 8, 23, "32 бита (4 байта). Диапазон до 3·10³⁸"), ("FP16", 5, 10, "16 бит (2 байта). Диапазон до 65 504"),
            ("BF16", 8, 7, "16 бит (2 байта). Диапазон как у FP32, точность ниже"), ("TF32", 8, 10, "19 бит, а не 32. Диапазон как у FP32")]
    items = [T("знак", 128, -62, 18, "#e03131"), T("range (диапазон)", 235, -62, 18, "#1971c2"),
             T("precision (точность)", 520, -62, 18, "#e8590c")]
    for i, (name, e, m, note) in enumerate(rows):
        y = i * 120
        items.append(T(name, 0, y + 14, 24, GRAY))
        x = 120
        items.append(N(f"s{i}", "", x, y, "r", u, 56))
        items.append(N(f"e{i}", f"{e} бит", x + u, y, "p", e * u, 56))
        items.append(N(f"m{i}", f"{m} бит", x + u + e * u, y, "q", m * u, 56))
        items.append(T(note, x, y + 62, 16, GRAY))
    return dict(items=items, edges=[])


D["ch07-number-formats"] = number_formats()

# ---------------------------------------------------------------- 7-7 partial finetuning vs adapters


def partial_vs_adapters():
    groups = [("1M", -9.5, -0.3), ("14M", -8.2, -0.3), ("26M", -5.1, -0.5), ("50M", -2.9, -0.3),
              ("100M", -0.5, None), ("300M", 0.0, None)]
    scale, zero = 32, 70
    items = [T("Падение точности относительно полного finetuning, % (значения прочитаны с графика книги)", 0, -80, 22, "#1971c2"),
             T("0 на линии = как полный finetuning. Ниже линии = хуже", 0, -40, 18, GRAY),
             N("zero", "", -10, zero - 2, "n", 1010, 4),
             T("число trainable-параметров на задачу", 900, zero - 100, 20, GRAY)]
    for i, (lab, top, ad) in enumerate(groups):
        x = i * 165
        if top != 0:
            items.append(N(f"t{i}", "", x, zero, "p", 60, -top * scale))
            items.append(T(fmt(top), x + 4, zero - top * scale + 4, 18, GRAY))
        else:
            items.append(T("0", x + 26, zero + 8, 18, GRAY))
        if ad is not None:
            items.append(N(f"d{i}", "", x + 66, zero, "q", 60, max(-ad * scale, 6)))
            items.append(T(fmt(ad), x + 70, zero + max(-ad * scale, 6) + 4, 18, GRAY))
        items.append(T(lab, x + 38, zero - 52, 20, GRAY))
    items += [N("lg1", "", 0, zero + 380, "p", 24, 24), T("дообучаем верхние слои", 34, zero + 378, 18, GRAY),
              N("lg2", "", 380, zero + 380, "q", 24, 24), T("адаптеры (Houlsby и др.)", 414, zero + 378, 18, GRAY)]
    return dict(items=items, edges=[])


D["ch07-partial-vs-adapters"] = partial_vs_adapters()

# ---------------------------------------------------------------- 7-8 adapter layer
D["ch07-adapter-houlsby"] = dict(items=[
    Z("Один блок Transformer с адаптерами", -20, -60, 470, 890),
    N("x1", "Multi-head attention\n(заморожен)", 0, 0, "n", 420, 80),
    N("ad1", "Adapter 1\n(обучается)", 0, 140, "g", 420, 80),
    N("n1", "Сложение с входом\nи layer norm", 0, 280, "n", 420, 80),
    N("x2", "Feedforward\n(заморожен)", 0, 420, "n", 420, 80),
    N("ad2", "Adapter 2\n(обучается)", 0, 560, "g", 420, 80),
    N("n2", "Сложение с входом\nи layer norm", 0, 700, "n", 420, 80),
    Z("Внутри adapter", 600, -60, 560, 890),
    N("d1", "Вход: вектор\nбольшой длины", 660, 0, "n", 440, 80),
    N("d2", "Down-project:\nсжимаем до малого вектора", 660, 160, "pu", 440, 90),
    N("d3", "Нелинейность", 660, 330, "pu", 440, 70),
    N("d4", "Up-project:\nвозвращаем исходную длину", 660, 480, "pu", 440, 90),
    N("d5", "Сложение с входом adapter\n(residual-связь)", 660, 640, "g", 440, 90),
], edges=[E("x1", "ad1"), E("ad1", "n1"), E("n1", "x2"), E("x2", "ad2"), E("ad2", "n2"),
          E("d1", "d2"), E("d2", "d3"), E("d3", "d4"), E("d4", "d5"), E("ad1", "d2", dashed=True)])

# ---------------------------------------------------------------- 7-9 soft prompt
D["ch07-soft-prompt"] = dict(items=[
    N("hp", "Hard prompt\n(текст):\n«Summarize the\nbook XYZ»", 0, 130, "n", 260, 140),
    N("emb", "Слой embeddings\n(веса модели)", 350, 150, "db", 280, 100),
    N("sp", "Soft prompt:\nобучаемые векторы\n[0,03 0,11 … 0,89]", 350, 330, "g", 280, 120),
    N("inp", "Вход модели:\nembeddings hard prompt\n+ soft prompt", 730, 150, "y", 320, 120),
    N("rest", "Остальные веса\nмодели\n(заморожены)", 1150, 150, "n", 260, 120),
    N("out", "Ответ", 1500, 170, "p", 160, 80),
    T("Soft prompt учится через backpropagation. Человек не может его прочитать.", 350, 480, 18),
    T("Hard prompt пишет человек. Он не обучается.", 0, 300, 18),
], edges=[E("hp", "emb"), E("emb", "inp"), E("sp", "inp", "обучаем"), E("inp", "rest"), E("rest", "out")])

# ---------------------------------------------------------------- 7-10 PEFT issues


def hbars(prefix, title, rows, scale, x0=300, hl=0):
    items = [T(title, 0, -60, 22, "#1971c2")]
    for i, (label, v) in enumerate(rows):
        y = i * 70
        items.append(T(label, 0, y + 12, 20, GRAY))
        items.append(N(f"{prefix}{i}", "", x0, y, "p" if i == hl else "n", max(v * scale, 6), 50))
        items.append(T(str(v), x0 + max(v * scale, 6) + 14, y + 12, 20, GRAY))
    return items


D["ch07-peft-issues"] = dict(items=hbars(
    "i", "Issues в репозитории huggingface/peft (октябрь 2024, значения прочитаны с графика)",
    [("LoRA", 720), ("QLoRA", 65), ("prompt tuning", 30), ("P-Tuning", 28), ("prefix-tuning", 20)], 0.62)
    + [T("LoRA сильно впереди. Число issues служит грубым показателем популярности метода.", 0, 380, 18)], edges=[])

# ---------------------------------------------------------------- PEFT map (our own)
D["ch07-peft-map"] = dict(items=[
    N("root", "Finetuning", 600, 0, "n", 260, 70),
    N("full", "Full finetuning\nобновляем все параметры", 0, 150, "r", 330, 90),
    N("part", "Partial finetuning\nучим часть слоёв.\nПараметрически неэффективен", 380, 150, "y", 360, 110),
    N("peft", "PEFT\nмало trainable-параметров,\nкачество близко к полному", 880, 150, "g", 400, 110),
    N("ad", "Adapter-based\n(additive): добавляем\nмодули к модели", 560, 340, "g", 330, 110),
    N("sp", "Soft prompt-based:\nдобавляем обучаемые\nтокены-векторы", 1130, 340, "g", 360, 110),
    N("a1", "Houlsby adapters,\nBitFit, IA3", 330, 540, "n", 270, 90),
    N("a2", "LoRA (самый\nпопулярный), LongLoRA", 640, 540, "p", 290, 90),
    N("a3", "QLoRA: LoRA + 4-bit\nвеса базовой модели", 960, 540, "pu", 300, 90),
    N("s1", "prefix-tuning,\nP-tuning,\nprompt tuning", 1330, 540, "n", 250, 110),
], edges=[E("root", "full"), E("root", "part"), E("root", "peft"), E("peft", "ad"), E("peft", "sp"),
          E("ad", "a1"), E("ad", "a2"), E("ad", "a3"), E("sp", "s1"), E("a2", "a3", dashed=True)])

# ---------------------------------------------------------------- 7-11 LoRA
D["ch07-lora"] = dict(items=[
    N("prev", "Предыдущий\nслой", 0, 0, "n", 200, 90),
    N("wnew", "W'  (n × m)\nновая матрица для модели", 300, 0, "p", 360, 100),
    N("next", "Следующий\nслой", 760, 0, "n", 200, 90),
    N("wab", "(α / r) · A × B\nn × m, добавка", 80, 200, "y", 300, 100),
    N("plus", "+", 460, 215, "n", 70, 70, "ellipse"),
    N("w", "W  (n × m)\nзаморожена", 640, 190, "n", 280, 100),
    N("a", "A  (n × r)\nобучается", 0, 400, "g", 240, 100),
    N("mul", "×", 340, 415, "n", 70, 70, "ellipse"),
    N("b", "B  (r × m)\nобучается", 500, 400, "g", 300, 100),
    T("r — rank: размер «узкого места». Чем меньше r, тем меньше параметров.", 0, 560, 18),
], edges=[E("prev", "wnew"), E("wnew", "next"), E("a", "mul"), E("b", "mul"), E("mul", "wab"),
          E("wab", "plus"), E("w", "plus"), E("plus", "wnew")])

# ---------------------------------------------------------------- 7-12 multi-LoRA
D["ch07-multi-lora"] = dict(items=[
    N("w", "Одна базовая матрица W\n(16,8M параметров)\nобщая для всех клиентов", 0, 190, "n", 360, 130),
    N("a1", "Клиент 1: A₁, B₁\n65 536 параметров", 560, 0, "g", 380, 90),
    N("a2", "Клиент 2: A₂, B₂\n65 536 параметров", 560, 230, "g", 380, 90),
    N("a3", "Клиенты 3 … 100:\nещё 98 пар (A, B)", 560, 460, "g", 380, 90),
    N("res", "100 клиентов: 16,8M + 100 × 65 536 ≈ 23,3M параметров.\nПо отдельности W' для каждого клиента было бы 1,68B.", 0, 640, "y", 960, 100),
    T("При запросе подставляем нужный адаптер. Переключение быстрее: грузим только маленькую пару.", 0, 780, 18),
], edges=[E("w", "a1"), E("w", "a2"), E("w", "a3")])

# ---------------------------------------------------------------- 7-13 ensembling vs merging
D["ch07-ensemble-vs-merge"] = dict(items=[
    Z("Ensembling: объединяем ответы", -20, -60, 700, 780),
    N("ein", "Вход", 250, 0, "n", 140, 70),
    N("em1", "Модель 1", 0, 150, "y", 190, 70), N("em2", "Модель 2", 230, 150, "g", 190, 70), N("em3", "Модель 3", 460, 150, "pu", 190, 70),
    N("eo1", "Ответ 1", 0, 310, "y", 190, 70), N("eo2", "Ответ 2", 230, 310, "g", 190, 70), N("eo3", "Ответ 3", 460, 310, "pu", 190, 70),
    N("ec", "Объединяем ответы\n(голосование или модуль ML)", 100, 480, "n", 450, 90),
    N("ef", "Итоговый ответ\n(3 вызова модели на запрос)", 100, 630, "p", 450, 80),
    Z("Model merging: объединяем веса", 780, -60, 700, 780),
    N("mm1", "Модель 1", 800, 150, "y", 190, 70), N("mm2", "Модель 2", 1030, 150, "g", 190, 70), N("mm3", "Модель 3", 1260, 150, "pu", 190, 70),
    N("mc", "Объединяем параметры\n(среднее, SLERP, слои ...)", 900, 330, "n", 450, 90),
    N("mm", "Слитая модель (один набор весов;\nможно дообучить дальше)", 900, 490, "g", 450, 90),
    N("min", "Вход", 800, 640, "n", 140, 70),
    N("mo", "Ответ\n(1 вызов модели)", 1100, 630, "p", 250, 90),
], edges=[E("ein", "em1"), E("ein", "em2"), E("ein", "em3"), E("em1", "eo1"), E("em2", "eo2"), E("em3", "eo3"),
          E("eo1", "ec"), E("eo2", "ec"), E("eo3", "ec"), E("ec", "ef"),
          E("mm1", "mc"), E("mm2", "mc"), E("mm3", "mc"), E("mc", "mm"), E("mm", "mo"), E("min", "mo")])

# ---------------------------------------------------------------- 7-14 three merge approaches


def merge_approaches():
    items, bh, bw = [], 36, 190
    row_y = [0, 230, 460]
    titles = ["Summing: складываем веса слоёв", "Layer stacking: ставим слои друг на друга", "Concatenation: склеиваем параметры"]
    for r, y in enumerate(row_y):
        items.append(T(titles[r], 0, y - 40, 22, GRAY))
        for i in range(3):
            items.append(N(f"l{r}{i}", f"слой {i + 1}", 0, y + i * (bh + 8), "p", bw, bh))
            items.append(N(f"m{r}{i}", f"слой {i + 1}", 330, y + i * (bh + 8), "y", bw, bh))
        items.append(T("+", 250, y + 36, 40, GRAY))
        items.append(T("→", 580, y + 36, 40, GRAY))
    # summing result
    for i in range(3):
        items.append(N(f"r0{i}", f"слой {i + 1} = сумма", 680, row_y[0] + i * (bh + 8), "pu", 260, bh))
    # stacking result: четыре слоя вперемешку
    order = [("p", "слой 1 (модель 1)"), ("y", "слой 2 (модель 2)"), ("p", "слой 3 (модель 1)"), ("y", "слой 3 (модель 2)")]
    for i, (k, t) in enumerate(order):
        items.append(N(f"r1{i}", t, 680, row_y[1] + i * (bh + 8) - 10, k, 260, bh))
    # concatenation result: слои шире
    for i in range(3):
        items.append(N(f"r2{i}", f"слой {i + 1}: часть 1", 680, row_y[2] + i * (bh + 8), "p", 200, bh))
        items.append(N(f"r2b{i}", "часть 2", 884, row_y[2] + i * (bh + 8), "y", 150, bh))
    items.append(T("Размер слоя не меняется", 960, row_y[0] + 40, 18, GRAY))
    items.append(T("Нужен ещё finetuning", 960, row_y[1] + 50, 18, GRAY))
    items.append(T("Параметров становится больше", 1060, row_y[2] + 40, 18, GRAY))
    return dict(items=items, edges=[])


D["ch07-merge-approaches"] = merge_approaches()

# ---------------------------------------------------------------- 7-15 average merge


def merge_average():
    m1 = [0.8, -0.2, 0.1, 0.5, -0.6, 0.3]
    m2 = [0.2, 0.4, -0.1, 0.1, 0.2, -0.3]
    avg = [round((a + b) / 2, 2) for a, b in zip(m1, m2)]
    items = [T("Модель 1", 0, 20, 22, "#1971c2"), T("Модель 2", 0, 170, 22, "#f08c00"), T("Среднее", 0, 345, 22, "#2f9e44"),
             T("+", 100, 85, 40, GRAY), T("↓  среднее: (a + b) / 2", 20, 240, 26, GRAY)]
    for i in range(6):
        x = 190 + i * 130
        items.append(N(f"a{i}", fmt(m1[i]), x, 0, "p", 110, 70, "ellipse"))
        items.append(N(f"b{i}", fmt(m2[i]), x, 150, "y", 110, 70, "ellipse"))
        items.append(N(f"c{i}", fmt(avg[i]), x, 330, "g", 110, 70, "ellipse"))
    items.append(T("Числа придуманы нами: каждый параметр одной модели усредняется с таким же параметром другой.", 0, 440, 18))
    return dict(items=items, edges=[])


D["ch07-merge-average"] = merge_average()

# ---------------------------------------------------------------- 7-16 SLERP


def slerp_diagram():
    cx, cy, R = 330, 330, 260
    pos = lambda deg, r=R: (cx + r * math.cos(math.radians(deg)), cy - r * math.sin(math.radians(deg)))
    items = [N("sph", "", cx - R, cy - R, "n", 2 * R, 2 * R, "ellipse")]
    for deg in (90, 80, 70, 60, 40, 30, 20, 10):
        x, y = pos(deg)
        items.append(N(f"d{deg}", "", x - 7, y - 7, "r", 14, 14, "ellipse"))
    x1, y1 = pos(100)
    x2, y2 = pos(0)
    xm, ym = pos(50)
    items += [N("o", "", cx - 9, cy - 9, "pu", 18, 18, "ellipse"),
              N("t1", "", x1 - 14, y1 - 14, "p", 28, 28, "ellipse"),
              N("t2", "", x2 - 14, y2 - 14, "p", 28, 28, "ellipse"),
              N("m", "", xm - 15, ym - 15, "g", 30, 30, "ellipse"),
              T("t₁", x1 - 62, y1 - 8, 24, "#1971c2"), T("t₂", x2 + 22, y2 - 12, 24, "#1971c2"),
              T("m", xm + 24, ym - 40, 24, "#2f9e44"),
              T("Красные точки: кратчайший\nпуть по поверхности сферы", 640, 130, 20, "#e03131"),
              T("Зелёная точка m: слитый вектор.\nКоэффициент 0,5 ставит её\nровно посередине пути.", 640, 250, 20, "#2f9e44"),
              T("Коэффициент < 0,5: ближе к t₁.\nКоэффициент > 0,5: ближе к t₂.", 640, 400, 20, GRAY),
              T("Сливаем только два вектора за раз. Для трёх: сначала A и B, потом результат и C.", 0, 640, 18)]
    return dict(items=items, edges=[E("o", "t1"), E("o", "t2"), E("o", "m")])


D["ch07-slerp"] = slerp_diagram()

# ---------------------------------------------------------------- 7-17 task vector pruning


def pruning_chart():
    xs = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    vals = [54, 71, 72.5, 73.5, 74, 74.5, 74, 74, 73.5, 74, 73.5]
    base, scale, floor_ = 400, 14, 50
    items = [T("Среднее качество слитой модели при разной доле сохранённых изменений (значения прочитаны с графика, ось от 50)", 0, -70, 20, "#1971c2")]
    for i, (x, v) in enumerate(zip(xs, vals)):
        h = (v - floor_) * scale
        items.append(N(f"b{i}", "", i * 95, base - h, "r" if i == 0 else ("g" if x >= 20 else "p"), 70, h))
        items.append(T(fmt(v), i * 95 + 8, base - h - 28, 18, GRAY))
        items.append(T(f"{x}%", i * 95 + 14, base + 10, 18, GRAY))
    items.append(T("доля самых больших изменений task vector, которую оставили (остальные вернули к значениям базовой модели)", 0, base + 50, 18))
    items.append(T("Оставить 20% изменений почти так же хорошо, как оставить все 100%.", 0, base + 90, 20, "#2f9e44"))
    return dict(items=items, edges=[])


D["ch07-task-vector-pruning"] = pruning_chart()

# ---------------------------------------------------------------- task vectors (our own)
D["ch07-task-vectors"] = dict(items=[
    N("base", "Базовая модель\nW₀", 560, 0, "n", 280, 90),
    N("fa", "Дообучена на A\nW_A", 100, 190, "p", 280, 90),
    N("fb", "Дообучена на B\nW_B", 1020, 190, "p", 280, 90),
    N("da", "Task vector A\nΔ_A = W_A − W₀", 100, 360, "y", 300, 100),
    N("db", "Task vector B\nΔ_B = W_B − W₀", 1000, 360, "y", 300, 100),
    N("cmb", "Комбинируем task vectors:\nсумма, среднее или разность", 480, 360, "pu", 440, 100),
    N("r1", "W₀ + Δ_A + Δ_B\nобе способности", 0, 590, "g", 340, 100),
    N("r2", "W₀ + ½(Δ_A + Δ_B)\nсреднее: обе правки\nослаблены", 480, 590, "p", 440, 120),
    N("r3", "W₀ + Δ_A − Δ_B\nубираем способность B", 1000, 590, "r", 400, 100),
], edges=[E("base", "fa", "finetuning"), E("base", "fb", "finetuning"), E("fa", "da", "− W₀"), E("fb", "db", "− W₀"),
          E("da", "cmb"), E("db", "cmb"), E("cmb", "r1"), E("cmb", "r2"), E("cmb", "r3")])

# ---------------------------------------------------------------- 7-18 MoE upcycling
D["ch07-moe-upcycling"] = dict(items=[
    Z("Исходный dense-блок", -20, -60, 1700, 190),
    N("t1", "Layer norm", 0, 0, "n", 200, 70), N("t2", "Attention", 270, 0, "y", 200, 70),
    N("t3", "Layer norm", 540, 0, "n", 200, 70), N("t4", "MLP", 1090, 0, "g", 200, 70),
    Z("Блок MoE после upcycling (пунктир: копируем веса)", -20, 190, 1700, 560),
    N("u1", "Layer norm", 0, 400, "n", 200, 70), N("u2", "Attention", 270, 400, "y", 200, 70),
    N("u3", "Layer norm", 540, 400, "n", 200, 70),
    N("rt", "Router\n(новый, обучается\nс нуля)", 810, 385, "r", 240, 100),
    N("e1", "MLP 1 (копия)", 1090, 270, "g", 220, 70), N("e2", "MLP 2 (копия)", 1090, 400, "g", 220, 70),
    N("e3", "MLP E (копия)", 1090, 530, "g", 220, 70),
    N("ws", "Weighted\nsum", 1400, 385, "pu", 200, 100),
    T("Остальные слои копируем как есть. MLP копируем E раз, router обучаем, затем дообучаем всю модель.", 0, 680, 18),
], edges=[E("t1", "t2"), E("t2", "t3"), E("t3", "t4"),
          E("u1", "u2"), E("u2", "u3"), E("u3", "rt"), E("rt", "e1"), E("rt", "e2"), E("rt", "e3"),
          E("e1", "ws"), E("e2", "ws"), E("e3", "ws"),
          E("t1", "u1", dashed=True), E("t2", "u2", dashed=True), E("t3", "u3", dashed=True),
          E("t4", "e1", "E копий", dashed=True)])

# ---------------------------------------------------------------- 7-19 depth up-scaling
D["ch07-depth-scaling"] = dict(items=[
    N("o", "Исходная модель\n32 слоя", 0, 150, "n", 260, 100),
    N("ca", "Копия A:\nслои 1–24\n(убрали 8 верхних)", 380, 0, "p", 290, 120),
    N("cb", "Копия B:\nслои 9–32\n(убрали 8 нижних)", 380, 300, "p", 290, 120),
    N("st", "Сшивка: слои A,\nзатем слои B.\n24 + 24 = 48 слоёв", 790, 140, "y", 290, 120),
    N("ct", "Continued\npre-training", 1190, 150, "pu", 250, 100),
    N("fin", "Готовая модель\n48 слоёв", 1550, 150, "g", 240, 100),
    T("Шаг 1: depthwise scaling (масштабирование в глубину)", 380, -60, 20, GRAY),
    T("Шаг 2: восстанавливаем качество", 1190, 100, 18, GRAY),
], edges=[E("o", "ca", "копия"), E("o", "cb", "копия"), E("ca", "st"), E("cb", "st"), E("st", "ct"), E("ct", "fin")])

# ---------------------------------------------------------------- 7-20 LoRA concatenation
D["ch07-lora-concat"] = dict(items=[
    Z("Adapter 1 (rank r₁)", -20, -60, 330, 260),
    N("a1", "A₁\nn × r₁", 20, 0, "p", 120, 80), N("b1", "B₁\nr₁ × m", 160, 100, "p", 120, 80),
    Z("Adapter 2 (rank r₂)", -20, 250, 330, 260),
    N("a2", "A₂\nn × r₂", 20, 310, "q", 120, 80), N("b2", "B₂\nr₂ × m", 160, 410, "q", 120, 80),
    N("cat", "Concatenate:\nA₁ и A₂ рядом,\nB₁ и B₂ друг под другом", 430, 150, "n", 360, 130),
    Z("Слитый adapter (rank r₁ + r₂)", 900, 20, 560, 440),
    N("ma", "[A₁ | A₂]\nn × (r₁ + r₂)", 960, 80, "y", 300, 100),
    N("mb", "[B₁ ; B₂]\n(r₁ + r₂) × m", 960, 230, "y", 300, 100),
    T("Результат равен A₁B₁ + A₂B₂.\nПараметров ровно столько,\nсколько в двух адаптерах.", 930, 360, 18, "#e03131"),
], edges=[E("a1", "cat"), E("a2", "cat"), E("cat", "ma"), E("cat", "mb")])

# ---------------------------------------------------------------- memory breakdown (our own, numbers from ch07_memory_calculator.py)


def memory_breakdown():
    scale, x0 = 7, 440
    rows = [("Полный finetuning,\nAdam, fp16", 14, 14, 28, "56 ГБ"),
            ("Полный finetuning,\nSGD без состояния", 14, 14, 0, "28 ГБ"),
            ("LoRA r=8,\nвеса fp16", 14, 0.05, 0, "14,1 ГБ"),
            ("QLoRA r=8,\nвеса int4", 3.5, 0.05, 0, "3,6 ГБ")]
    items = [T("Память для модели 7B при finetuning, ГБ (без activations; числа из ch07_memory_calculator.py)", 0, -110, 20, "#1971c2"),
             N("l24", "", x0 + 24 * scale - 2, -30, "y", 4, 460), T("24 ГБ\nобычная GPU", x0 + 24 * scale - 50, -85, 16, "#f08c00"),
             N("l80", "", x0 + 80 * scale - 2, -30, "r", 4, 460), T("80 ГБ\nмощная GPU", x0 + 80 * scale - 50, -85, 16, "#e03131")]
    for i, (name, w, g, o, total) in enumerate(rows):
        y = i * 100
        items.append(T(name, 0, y + 6, 20, GRAY))
        x = x0
        items.append(N(f"w{i}", "", x, y, "p", w * scale, 56))
        x += w * scale
        if g:
            items.append(N(f"g{i}", "", x, y, "y", max(g * scale, 4), 56))
            x += max(g * scale, 4)
        if o:
            items.append(N(f"o{i}", "", x, y, "r", o * scale, 56))
            x += o * scale
        lx = x + 14
        line24 = x0 + 24 * scale
        if lx < line24 + 10 and lx + 110 > line24:   # подпись не должна лежать на вертикальной линии
            lx = line24 + 16
        items.append(T(total, lx, y + 14, 22, GRAY))
    items += [N("lg1", "", 0, 470, "p", 24, 24), T("веса модели", 34, 468, 18, GRAY),
              N("lg2", "", 200, 470, "y", 24, 24), T("gradients", 234, 468, 18, GRAY),
              N("lg3", "", 350, 470, "r", 24, 24), T("optimizer states (Adam)", 384, 468, 18, GRAY)]
    return dict(items=items, edges=[])


D["ch07-memory-breakdown"] = memory_breakdown()

# ---------------------------------------------------------------- quantization map (our own)
D["ch07-quantization-map"] = dict(items=[
    N("root", "Quantization:\nменьше бит на значение", 560, 0, "n", 340, 90),
    N("what", "Что квантуем:\nвеса (чаще) и\nactivations (реже)", 0, 190, "y", 300, 120),
    N("ptq", "PTQ: после обучения.\nСамый частый вариант.\nВ PyTorch за несколько строк", 380, 190, "g", 380, 120),
    N("qat", "QAT: во время обучения\nмодель симулирует низкую\nточность. Время не падает", 840, 190, "p", 400, 120),
    N("low", "Обучение в низкой точности:\nmixed precision, INT8.\nТрудно: backpropagation\nчувствителен к ошибкам", 1320, 190, "pu", 400, 140),
    N("fmt", "Шкала форматов:\nFP32 → FP16/BF16 → INT8 → INT4 → 1,58 бита", 0, 440, "n", 700, 80),
    Z("Пределы и риски", 780, 400, 960, 200),
    N("lim", "Предел: меньше 1 бита\nна значение нельзя.\nBitNet b1.58 — около 1,58", 800, 450, "r", 400, 110),
    N("risk", "Риск: ошибки округления\nнакапливаются, значения вне\nдиапазона становятся inf", 1260, 450, "r", 440, 110),
], edges=[E("root", "what"), E("root", "ptq"), E("root", "qat"), E("root", "low"), E("what", "fmt", dashed=True)])

# ---------------------------------------------------------------- tactics paths (our own)
D["ch07-tactics-paths"] = dict(items=[
    Z("Путь progression: от дешёвого к лучшему", -20, -60, 1620, 230),
    N("p1", "1. Дешёвая модель:\nпроверяем код\nfinetuning", 0, 0, "n", 330, 110),
    N("p2", "2. Средняя модель:\nпроверяем данные (loss\nпадает с ростом данных?)", 400, 0, "y", 400, 110),
    N("p3", "3. Лучшая модель:\nищем потолок\nкачества", 870, 0, "g", 300, 110),
    N("p4", "4. Прогон на всех:\nкривая цена и качество,\nвыбор модели", 1230, 0, "p", 330, 110),
    Z("Путь distillation: от лучшего к дешёвому", -20, 250, 1620, 230),
    N("d1", "1. Сильная модель +\nмалый датасет:\nлучшая модель", 0, 310, "g", 360, 110),
    N("d2", "2. Она генерирует\nбольше обучающих\nданных", 480, 310, "y", 340, 110),
    N("d3", "3. Дешёвая модель\nучится на новых\nданных", 940, 310, "p", 340, 110),
], edges=[E("p1", "p2"), E("p2", "p3"), E("p3", "p4"), E("d1", "d2"), E("d2", "d3")])

# ---------------------------------------------------------------- loss curves guide (our own)
D["ch07-loss-curves-guide"] = dict(items=[
    T("Что видно на кривых loss", 0, -50, 22, "#1971c2"), T("Что это значит", 520, -50, 22, "#1971c2"),
    T("Что делать", 1040, -50, 22, "#1971c2"),
    N("s1", "Training loss сильно\nскачет вверх и вниз", 0, 0, "r", 440, 90),
    N("c1", "Learning rate\nслишком велик", 520, 0, "n", 420, 90),
    N("a1", "Уменьшить learning rate", 1040, 0, "g", 440, 90),
    N("s2", "Loss стабилен, но падает\nочень медленно", 0, 150, "y", 440, 90),
    N("c2", "Learning rate\nслишком мал", 520, 150, "n", 420, 90),
    N("a2", "Увеличивать, пока loss стабилен", 1040, 150, "g", 440, 90),
    N("s3", "Training loss падает,\nvalidation loss растёт", 0, 300, "r", 440, 90),
    N("c3", "Overfitting: модель\nзапоминает данные", 520, 300, "n", 420, 90),
    N("a3", "Уменьшить число epochs", 1040, 300, "g", 440, 90),
    N("s4", "Оба loss падают\nравномерно", 0, 450, "g", 440, 90),
    N("c4", "Модель ещё\nне насытилась", 520, 450, "n", 420, 90),
    N("a4", "Больше epochs и данных", 1040, 450, "g", 440, 90),
], edges=[E("s1", "c1"), E("c1", "a1"), E("s2", "c2"), E("c2", "a2"), E("s3", "c3"), E("c3", "a3"), E("s4", "c4"), E("c4", "a4")])

if __name__ == "__main__":
    run_all(D)
