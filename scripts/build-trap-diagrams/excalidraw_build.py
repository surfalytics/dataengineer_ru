#!/usr/bin/env python3
"""Build Excalidraw diagrams for the Escaping the Build Trap summary.

Needs the local Excalidraw canvas server on http://127.0.0.1:3456.
Run from the repo root:

    python3 scripts/build-trap-diagrams/excalidraw_build.py            # all diagrams
    python3 scripts/build-trap-diagrams/excalidraw_build.py ch11 ch15  # only some

Each diagram gets its own scene `dataengineer_ru/bt-<name>` and a PNG in
public/assets/escaping-the-build-trap/. Then run compress.mjs to shrink PNGs.
"""
import base64
import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:3456"
OUT = "public/assets/escaping-the-build-trap"
PREFIX = "dataengineer_ru/bt-"

# Style from .claude/skills/diagrams/SKILL.md
S = {
    "main": ("#a5d8ff", "#1971c2"),
    "good": ("#b2f2bb", "#2f9e44"),
    "bad": ("#ffc9c9", "#e03131"),
    "note": ("#ffec99", "#f08c00"),
    "store": ("#99e9f2", "#0c8599"),
    "neutral": ("#e9ecef", "#868e96"),
    "etl": ("#eebefa", "#9c36b5"),
}
FONT = 6


BOXES = {}  # id -> (x, y, w, h); filled by N(), used by E()


def N(id, x, y, text, style="main", w=250, h=100, size=20, dashed=False):
    """Box with a centered label."""
    fill, stroke = S[style]
    BOXES[id] = (x, y, w, h)
    el = {
        "id": id, "type": "rectangle", "x": x, "y": y, "width": w, "height": h,
        "backgroundColor": fill, "strokeColor": stroke, "fillStyle": "solid",
        "roughness": 1, "strokeWidth": 2,
        "strokeStyle": "dashed" if dashed else "solid",
    }
    if text:
        el["label"] = {"text": text, "fontSize": size, "fontFamily": FONT,
                       "strokeColor": stroke}
    return el


def E(a, b, dashed=False, color="#1e1e1e", gap=8):
    """Arrow from the edge of box a to the edge of box b."""
    ax, ay, aw, ah = BOXES[a]
    bx, by, bw, bh = BOXES[b]
    acx, acy, bcx, bcy = ax + aw / 2, ay + ah / 2, bx + bw / 2, by + bh / 2
    dx, dy = bcx - acx, bcy - acy
    if abs(dx) * ah >= abs(dy) * aw:  # mostly horizontal
        sx = ax + aw + gap if dx > 0 else ax - gap
        ex = bx - gap if dx > 0 else bx + bw + gap
        sy, ey = acy, bcy
        if abs(acy - bcy) < max(ah, bh) / 2:  # same row: keep the arrow flat
            sy = ey = (max(ay, by) + min(ay + ah, by + bh)) / 2
    else:  # mostly vertical
        sy = ay + ah + gap if dy > 0 else ay - gap
        ey = by - gap if dy > 0 else by + bh + gap
        sx, ex = acx, bcx
        if abs(acx - bcx) < max(aw, bw) / 2:  # same column
            sx = ex = (max(ax, bx) + min(ax + aw, bx + bw)) / 2
    return {
        "type": "arrow", "x": sx, "y": sy, "width": abs(ex - sx), "height": abs(ey - sy),
        "points": [[0, 0], [ex - sx, ey - sy]],
        "startElementId": a, "endElementId": b, "strokeColor": color,
        "roughness": 1, "strokeWidth": 2,
        "strokeStyle": "dashed" if dashed else "solid",
    }


def T(x, y, text, size=20, color="#1e1e1e"):
    """Free text."""
    return {"type": "text", "x": x, "y": y, "text": text, "fontSize": size,
            "fontFamily": FONT, "strokeColor": color}


def TITLE(text):
    return T(40, 20, text, 28)


def NOTE(y, text):
    return T(40, y, text, 18, "#868e96")


# ---------------------------------------------------------------- diagrams

def ch00_book_map():
    parts = [
        ("p1", "I. Build Trap\nобмен ценностью,\nпроект и продукт", "bad"),
        ("p2", "II. Роль PM\nархетипы, карьера,\nкоманды", "main"),
        ("p3", "III. Стратегия\nvision, intents,\nпортфель", "etl"),
        ("p4", "IV. Процесс\nProduct Kata,\nметрики, эксперименты", "note"),
        ("p5", "V. Product-led\nкоммуникация,\nстимулы, бюджет", "good"),
    ]
    el = [TITLE("Escaping the Build Trap: пять частей книги")]
    for i, (id, text, st) in enumerate(parts):
        el.append(N(id, 40 + i * 290, 90, text, st, w=250, h=140))
    for a, b in zip(parts, parts[1:]):
        el.append(E(a[0], b[0]))
    el.append(NOTE(260, "Сквозной пример: компания Marquetly уходит от output к outcome."))
    return el


def ch01_value_exchange():
    return [
        TITLE("Обмен ценностью: клиент и компания"),
        N("cust", 40, 90, "Клиент\nпроблемы, желания,\nпотребности", "main", w=280, h=120),
        N("comp", 700, 90, "Компания\nпродукт или сервис\nрешает проблему", "etl", w=280, h=120),
        {"type": "arrow", "x": 692, "y": 125, "width": 364, "height": 0,
         "points": [[0, 0], [-364, 0]], "strokeColor": "#1971c2", "strokeWidth": 2, "roughness": 1},
        T(400, 92, "проблема решена", 18, "#1971c2"),
        {"type": "arrow", "x": 328, "y": 180, "width": 364, "height": 0,
         "points": [[0, 0], [364, 0]], "strokeColor": "#9c36b5", "strokeWidth": 2, "roughness": 1},
        T(340, 188, "ценность назад: деньги, данные,\nзнания, продвижение", 18, "#9c36b5"),
        N("out", 40, 270, "Output: что сделали\n\nфичи, релизы,\nсданные сроки", "bad", w=440, h=180),
        N("res", 540, 270, "Outcome: что изменилось\n\nпроблема клиента решена,\nбизнес получил ценность", "good", w=440, h=180),
        NOTE(475, "Build trap: компания измеряет успех по output, а не по outcome."),
    ]


def ch03_project_vs_product():
    steps = ["Define", "Build", "Deploy", "Celebrate", "Move on"]
    el = [TITLE("Проект заканчивается, продукт живёт"),
          T(40, 80, "Проектный цикл: после релиза команда уходит", 20, "#e03131")]
    for i, s in enumerate(steps):
        el.append(N(f"p{i}", 40 + i * 210, 120, s, "neutral" if i == 4 else "bad", w=170, h=80))
    for i in range(4):
        el.append(E(f"p{i}", f"p{i+1}"))
    el.append(T(40, 250, "Продуктовый цикл: релиз — это гипотеза, цикл идёт до цели", 20, "#2f9e44"))
    loop = [("q1", "Цель и метрика\n(outcome)", "good"), ("q2", "Изучить\nпроблему", "good"),
            ("q3", "Эксперимент\nили релиз", "good"), ("q4", "Измерить:\nцель достигнута?", "main")]
    for i, (id, t, st) in enumerate(loop):
        el.append(N(id, 40 + i * 270, 290, t, st, w=220, h=90))
    for a, b in zip(loop, loop[1:]):
        el.append(E(a[0], b[0]))
    el.append(N("back", 380, 440, "Нет: что узнали? Новый цикл", "neutral", w=340, h=70, dashed=True))
    el.append(E("q4", "back", dashed=True, color="#1971c2"))
    el.append(E("back", "q1", dashed=True, color="#1971c2"))
    return el


def ch04_company_types():
    return [
        TITLE("Четыре типа компаний"),
        N("s", 40, 90, "Sales-led\nroadmap задают\nсделки и обещания", "bad", w=280, h=130),
        N("v", 360, 90, "Visionary-led\nвсё держится\nна одном лидере", "bad", w=280, h=130),
        N("t", 680, 90, "Technology-led\nновая технология\nбез рынка", "bad", w=280, h=130),
        N("p", 200, 270, "Product-led\nрешения от бизнес-результата\nи успеха продукта", "good", w=600, h=120),
        E("s", "p", dashed=True), E("v", "p", dashed=True), E("t", "p", dashed=True),
        NOTE(420, "Первые три типа часто ведут в build trap."),
    ]


def ch06_pm_archetypes():
    return [
        TITLE("Три плохих архетипа продакт-менеджера"),
        N("a", 40, 90, "Mini-CEO\nдиктует решения,\nно власти нет", "bad", w=300, h=140),
        N("b", 380, 90, "Waiter\nпринимает заказы,\nнет цели и видения", "bad", w=300, h=140),
        N("c", 720, 90, "Former project\nmanager\nдумает «когда»,\nа не «почему»", "bad", w=300, h=140),
        N("g", 40, 280, "Нужно: PM владеет «почему».\nВедёт через влияние, а не через власть", "good", w=980, h=100),
        NOTE(405, "Waiter ведёт к product death cycle: делаем, что просят, без проверки."),
    ]


def ch07_great_pm():
    return [
        TITLE("Хороший PM работает на стыке трёх областей"),
        N("bus", 40, 90, "Business\nцели, деньги,\nрынок", "main", w=280, h=130),
        N("tech", 380, 90, "Technology\nчто возможно\nи сколько стоит", "etl", w=280, h=130),
        N("ux", 720, 90, "UX / дизайн\nпроблемы и\nповедение людей", "note", w=280, h=130),
        N("pm", 210, 280, "Product Manager\nвладеет «почему»: проблема и результат.\n«Что» решает вся команда", "good", w=620, h=130),
        E("bus", "pm"), E("tech", "pm"), E("ux", "pm"),
        NOTE(440, "Нужна грамотность (literate) в технологиях, а не свободное владение (fluent)."),
    ]


def ch08_pm_work_mix():
    rows = [("Associate PM / PM", 400, 220, 80), ("Senior PM", 300, 280, 120),
            ("Director of Product", 140, 320, 240), ("VP of Product", 70, 280, 350),
            ("CPO", 40, 200, 460)]
    el = [TITLE("Тип работы PM по уровням (пропорции условные)")]
    legend = [("Tactical: задачи на сейчас", "note"), ("Operational: roadmap", "main"),
              ("Strategic: куда идёт продукт", "etl")]
    for i, (t, st) in enumerate(legend):
        el.append(N(f"l{i}", 40 + i * 340, 80, "", st, w=30, h=30))
        el.append(T(80 + i * 340, 83, t, 18, S[st][1]))
    y = 140
    for name, a, b, c in rows:
        el.append(T(40, y + 20, name, 20))
        x = 270
        for w, st in ((a, "note"), (b, "main"), (c, "etl")):
            el.append(N(f"r{y}{x}", x, y, "", st, w=w, h=60))
            x += w
        y += 80
    el.append(NOTE(y + 10, "Чем выше уровень, тем больше стратегии и меньше тактики."))
    return el


def ch09_team_structures():
    return [
        TITLE("Как организовать продуктовые команды"),
        N("c", 40, 90, "По компонентам\nAPI, бэкенд, фронтенд.\nКоманда полирует\nсвой кусок", "bad", w=320, h=170),
        N("f", 400, 90, "По фичам\nпоиск, оплата, профиль.\nКоманда добавляет\nфичи", "note", w=320, h=170),
        N("v", 760, 90, "По value stream\nили целям.\nКоманда владеет\nрезультатом", "good", w=320, h=170),
        NOTE(290, "Value stream — все шаги, которые доставляют ценность клиенту."),
        NOTE(320, "Пример TransferWise: команды вокруг целей — удержание, новые валюты, новые клиенты."),
    ]


def ch10_strategy_metrics():
    return [
        TITLE("Стратегия → тактика → метрика"),
        N("s", 40, 90, "Стратегия\nкак выиграть", "etl", w=280, h=110),
        N("t", 400, 90, "Тактика\nчто делаем", "main", w=280, h=110),
        N("m", 760, 90, "Метрика\nкак узнаем,\nчто работает", "good", w=280, h=110),
        E("s", "t"), E("t", "m"),
        T(40, 240, "Пример Netflix:", 20, "#1e1e1e"),
        N("s1", 40, 280, "Персонализация", "etl", w=280, h=90),
        N("t1", 400, 280, "Оценки фильмов\nпользователями", "main", w=280, h=90),
        N("m1", 760, 280, "Доля клиентов, которые\nоценили много фильмов\nв первые недели", "good", w=280, h=90, size=18),
        E("s1", "t1"), E("t1", "m1"),
        NOTE(395, "Каждая метрика — готовое требование к данным: событие, окно, порог."),
    ]


def ch11_strategy_gaps():
    return [
        TITLE("Три разрыва между результатом, планом и действием (Bungay)"),
        N("res", 40, 110, "Результаты\nчего хотим", "good", w=260, h=90),
        N("plan", 420, 110, "Планы\nчто решили делать", "main", w=260, h=90),
        N("act", 800, 110, "Действия\nчто делают люди", "etl", w=260, h=90),
        E("res", "plan"), E("plan", "act"),
        T(305, 80, "knowledge gap", 18, "#e03131"),
        T(685, 80, "alignment gap", 18, "#e03131"),
        T(800, 215, "effects gap: действия дают не тот результат", 18, "#e03131"),
        N("k", 40, 270, "Knowledge gap\nНе просите больше деталей.\nОбъясните strategic intent,\nпросите только нужное", "note", w=320, h=170),
        N("a", 400, 270, "Alignment gap\nНе давайте детальных\nуказаний. Каждый уровень\nсам решает «как»", "note", w=320, h=170),
        N("e", 760, 270, "Effects gap\nНе добавляйте контроль.\nДайте командам свободу\nменять действия", "note", w=320, h=170),
        NOTE(465, "Итог: автономные команды внутри ясной стратегии. Так компания масштабируется."),
    ]


def ch12_strategy_levels():
    rows = [
        ("v", "Vision", "куда идёт компания", "etl", "Уровень компании"),
        ("i", "Strategic intents", "главные бизнес-цели", "main", "Уровень компании"),
        ("p", "Product initiatives", "проблемы клиентов для решения", "store", "Уровень продукта"),
        ("o", "Options", "варианты решений, ставки", "note", "Уровень продукта"),
    ]
    el = [TITLE("Четыре уровня развёртывания стратегии")]
    for i, (id, name, what, st, lvl) in enumerate(rows):
        y = 90 + i * 130
        el.append(N(id, 40, y, f"{name}\n{what}", st, w=400, h=90))
        el.append(T(490, y + 32, lvl, 20, "#495057"))
    for a, b in zip(rows, rows[1:]):
        el.append(E(a[0], b[0]))
    el.append(NOTE(620, "Горизонт: руководство — около 5 лет, менеджеры — год или квартал, команды — 2–4 недели."))
    return el


def ch15_kata_questions():
    plan = [("k1", "1. Какая цель?"), ("k2", "2. Где мы сейчас\nотносительно цели?"),
            ("k3", "3. Что главное\nпрепятствие?"), ("k4", "4. Как попробуем\nего убрать?")]
    el = [TITLE("Product Kata: вопросы на каждый цикл"),
          T(40, 75, "Планируем следующий шаг", 20, "#1971c2")]
    for i, (id, t) in enumerate(plan):
        el.append(N(id, 40 + i * 290, 110, t, "main", w=240, h=100))
    for a, b in zip(plan, plan[1:]):
        el.append(E(a[0], b[0]))
    el += [
        T(620, 240, "Разбираем итог", 20, "#2f9e44"),
        N("k5", 910, 280, "5. Что ожидаем?\n(гипотеза)", "good", w=240, h=100),
        N("k6", 620, 280, "6. Что произошло\nи что узнали?", "good", w=240, h=100),
        N("k7", 330, 280, "Цель достигнута?\nНет — новый цикл", "neutral", w=240, h=100),
        E("k4", "k5"), E("k5", "k6"), E("k6", "k7"), E("k7", "k1", dashed=True),
        NOTE(410, "Вопросы 1–4 планируют шаг. Вопросы 5–6 разбирают итог. Потом новый цикл."),
    ]
    return el


def ch16_metrics_frameworks():
    aarrr = ["Acquisition", "Activation", "Retention", "Referral", "Revenue"]
    heart = ["Happiness", "Engagement", "Adoption", "Retention", "Task success"]
    el = [TITLE("Два набора продуктовых метрик"),
          T(40, 75, "Pirate metrics (AARRR): путь пользователя", 20, "#1971c2")]
    for i, t in enumerate(aarrr):
        el.append(N(f"a{i}", 40 + i * 230, 110, t, "main", w=190, h=80))
    for i in range(4):
        el.append(E(f"a{i}", f"a{i+1}"))
    el.append(T(40, 225, "HEART: опыт пользователя", 20, "#f08c00"))
    for i, t in enumerate(heart):
        el.append(N(f"h{i}", 40 + i * 230, 260, t, "note", w=190, h=80))
    el.append(N("bal", 40, 390, "Retention — lagging: видно через месяцы. Leading: activation, happiness, engagement.\nПары метрик: растим acquisition, но retention не ниже порога", "neutral", w=1110, h=90))
    return el


def ch18_experiments():
    return [
        TITLE("Эксперименты, чтобы учиться"),
        N("c", 40, 90, "Concierge\nделаем вручную,\nклиент это знает", "main", w=320, h=150),
        N("w", 400, 90, "Wizard of Oz\nвыглядит как продукт,\nвнутри ручная работа", "etl", w=320, h=150),
        N("t", 760, 90, "Concept test\nмакет или видео\nвместо продукта", "note", w=320, h=150),
        N("r", 40, 290, "Build to learn, not to earn. MVP — минимум усилий, чтобы научиться.\nЗакрывайте цикл: скажите клиентам, когда и как тест закончится", "good", w=1040, h=90),
    ]


def ch19_definition_of_done():
    return [
        TITLE("Когда работа «готова»"),
        N("old", 40, 90, "Обычный Done\n\nкод и тесты готовы,\nрелиз вышел,\nзадача закрыта", "bad", w=500, h=230),
        N("new", 580, 90, "Done по книге\n\nкритерии успеха заданы до релиза,\nv1 — гипотеза,\nрезультат измерен и достигнут", "good", w=500, h=230),
        NOTE(345, "Для дата-команды: витрина готова, когда ей пользуются для решений."),
    ]


def ch20_roadmap_stages():
    st = [("s1", "Experiment\nстоит ли решать\nпроблему?", "neutral"),
          ("s2", "Alpha\nрешение нужно?\nможно закрыть", "note"),
          ("s3", "Beta\nмасштабируется?", "main"),
          ("s4", "Generally\nAvailable\nдля всех", "good")]
    el = [TITLE("Стадии на roadmap и ритм встреч")]
    for i, (id, t, s) in enumerate(st):
        el.append(N(id, 40 + i * 290, 90, t, s, w=240, h=120))
    for a, b in zip(st, st[1:]):
        el.append(E(a[0], b[0]))
    el += [
        N("m1", 40, 260, "Business review\nруководство,\nstrategic intents", "etl", w=340, h=120),
        N("m2", 420, 260, "Product initiative review\nлидеры продукта,\nпрогресс инициатив", "store", w=340, h=120),
        N("m3", 800, 260, "Release review\nкоманды,\nчто выходит и метрики", "main", w=340, h=120),
        NOTE(405, "Продажи обещают клиентам только GA или поздний Beta. Roadmap — не план с датами."),
    ]
    return el


def ch23_vc_budgeting():
    return [
        TITLE("Бюджет: годовой план или как инвестор"),
        T(40, 80, "Годовой бюджет", 20, "#e03131"),
        N("y", 40, 120, "Все деньги на год\nпо бизнес-кейсу.\nНе сделали обещанное —\nменьше денег", "bad", w=320, h=260),
        T(440, 80, "Как венчурный инвестор", 20, "#2f9e44"),
        N("b1", 440, 300, "Поиск\n~$50K", "neutral", w=200, h=80),
        N("b2", 690, 220, "Есть рынок\n~$250K\nпервая версия", "main", w=200, h=160),
        N("b3", 940, 120, "Продукт\nпринимают\nмиллионы\nна рост", "good", w=200, h=260),
        E("b1", "b2"), E("b2", "b3"),
        NOTE(405, "Каждый бюджет — на переход к следующей стадии. Не дошли — деньги уходят в другое место."),
    ]


def ch25_product_led_system():
    items = [("Outcome\nвместо output", "good"), ("Стратегия без\nгодового цикла", "main"),
             ("Эксперименты, безопасность,\nнаграды за обучение", "etl"), ("Бюджет\nкак у инвестора", "note"),
             ("Продукт вокруг\nклиента", "store"), ("Сильные лидеры\nи наставники для PM", "main")]
    el = [TITLE("Из чего состоит product-led компания")]
    for i, (t, s) in enumerate(items):
        el.append(N(f"i{i}", 40 + (i % 3) * 360, 90 + (i // 3) * 160, t, s, w=320, h=120))
    el.append(N("base", 40, 420, "Изменения начинаются с CEO. Marquetly шла к этому несколько лет", "neutral", w=1040, h=80))
    return el


def ch26_six_questions():
    q = ["1. Кто придумал\nпоследнюю фичу?", "2. Какой продукт\nвы последним закрыли?",
         "3. Когда вы говорили\nс клиентами?", "4. Какая у вас цель?",
         "5. Над чем вы\nсейчас работаете?", "6. Какие у вас\nпродакт-менеджеры?"]
    el = [TITLE("Шесть вопросов: компания product-led?")]
    for i, t in enumerate(q):
        el.append(N(f"q{i}", 40 + (i % 3) * 360, 90 + (i // 3) * 150, t, "main" if i < 3 else "good", w=320, h=110))
    el.append(NOTE(400, "Задавайте их на собеседовании. Ответы покажут, как компания работает."))
    return el


DIAGRAMS = {
    "ch00-book-map": ch00_book_map,
    "ch01-value-exchange": ch01_value_exchange,
    "ch03-project-vs-product": ch03_project_vs_product,
    "ch04-company-types": ch04_company_types,
    "ch06-pm-archetypes": ch06_pm_archetypes,
    "ch07-great-pm": ch07_great_pm,
    "ch08-pm-work-mix": ch08_pm_work_mix,
    "ch09-team-structures": ch09_team_structures,
    "ch10-strategy-metrics": ch10_strategy_metrics,
    "ch11-strategy-gaps": ch11_strategy_gaps,
    "ch12-strategy-levels": ch12_strategy_levels,
    "ch15-kata-questions": ch15_kata_questions,
    "ch16-metrics-frameworks": ch16_metrics_frameworks,
    "ch18-experiments": ch18_experiments,
    "ch19-definition-of-done": ch19_definition_of_done,
    "ch20-roadmap-stages": ch20_roadmap_stages,
    "ch23-vc-budgeting": ch23_vc_budgeting,
    "ch25-product-led-system": ch25_product_led_system,
    "ch26-six-questions": ch26_six_questions,
}

# ---------------------------------------------------------------- canvas API


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return json.loads(e.read() or b"{}")


def open_scene(name):
    res = call("POST", "/api/scenes", {"name": name})
    if not res.get("success"):
        call("POST", "/api/scenes/open", {"name": name})
        for el in call("GET", "/api/elements").get("elements", []):
            call("DELETE", f"/api/elements/{el['id']}")


def build(name, fn):
    open_scene(PREFIX + name)
    res = call("POST", "/api/elements/batch", {"elements": fn()})
    if not res.get("success"):
        raise SystemExit(f"{name}: batch failed: {res}")
    img = call("POST", "/api/export/image", {"format": "png", "scale": 2, "padding": 30})
    with open(f"{OUT}/{name}.png", "wb") as f:
        f.write(base64.b64decode(img["data"]))
    call("POST", "/api/scenes/save")
    print("ok", name)


if __name__ == "__main__":
    only = sys.argv[1:]
    for name, fn in DIAGRAMS.items():
        if not only or any(name.startswith(o) for o in only):
            build(name, fn)
