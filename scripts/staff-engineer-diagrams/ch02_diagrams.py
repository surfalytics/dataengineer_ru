#!/usr/bin/env python3
"""Chapter 2 (operating at Staff: what matters, strategy, quality) diagrams. Usage: ch02_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Figure "Quadrants of high and low impact by high and low effort" (no image in EPUB, redrawn from caption and text)
D["ch02-effort-impact"] = dict(items=[
    T("Польза высокая", -260, 70, 20, "#2f9e44"),
    T("Польза низкая", -260, 390, 20, "#e03131"),
    T("Мало усилий", 120, -60, 20, "#495057"),
    T("Много усилий", 780, -60, 20, "#495057"),
    N("easy_hi", "Лёгкое и важное\n\nв хорошей компании\nбыстро кончается", 0, 0, "g", 420, 180),
    N("hard_hi", "Трудное и важное\n\nсюда стоит идти:\nвыживание, рост людей,\nто, что можете только вы", 660, 0, "p", 420, 180),
    N("easy_lo", "Лёгкое и неважное:\nsnacking\n\npreening — такая же работа,\nно на виду у всех", 0, 340, "y", 420, 180),
    N("hard_lo", "Трудное и неважное:\nchasing ghosts\n\nновый руководитель чинит\nто, что сломано не здесь", 660, 340, "r", 420, 180),
], edges=[E("easy_hi", "hard_hi", "верный шаг"), E("easy_hi", "easy_lo", "соблазн")])

# own: five design docs -> strategy, five strategies -> vision
D["ch02-docs-strategy-vision"] = dict(items=[
    N("d1", "design doc 1", 0, 0, "n", 190, 70),
    N("d2", "design doc 2", 220, 0, "n", 190, 70),
    N("d3", "design doc 3", 440, 0, "n", 190, 70),
    N("d4", "design doc 4", 660, 0, "n", 190, 70),
    N("d5", "design doc 5", 880, 0, "n", 190, 70),
    N("st", "Стратегия\nобщие спорные решения\nи почему их так приняли", 335, 230, "p", 400, 120),
    T("Ещё 4 стратегии\nпишут так же", 800, 260, 18),
    N("vi", "Видение (vision)\nкартина на 2–3 года,\n1–2 страницы", 335, 560, "pu", 400, 120),
    T("Проверка видения: design doc двухлетней давности\nхуже, чем design doc прошлой недели", 0, 720, 18, "#495057"),
], edges=[E("d1", "st"), E("d2", "st"), E("d3", "st"), E("d4", "st"), E("d5", "st"),
          E("st", "vi", "5 стратегий +\nпрогноз")])

# own: the toolkit of quality approaches, from cheap to heavy
D["ch02-quality-staircase"] = dict(items=[
    T("От дешёвого к тяжёлому. Следующий шаг — только когда прежний не справляется", 0, -60, 20, "#495057"),
    N("hot", "1. Hot spots\nчинить то, что\nболит сейчас", 0, 0, "g", 270, 130),
    N("bp", "2. Best practices\nкогда hot spots\nне успеваете чинить", 330, 0, "g", 270, 130),
    N("lev", "3. Leverage points\nкогда хочется\nвторую практику сразу", 660, 0, "p", 270, 130),
    N("vec", "4. Technical vectors\nкогда нужно согласие\nвсей организации", 990, 0, "p", 270, 130),
    N("mes", "5. Измерить\nкогда всего\nэтого мало", 990, 260, "y", 270, 130),
    N("team", "6. Команда\nтехнического качества\n3–6 человек", 660, 260, "q", 270, 130),
    N("prog", "7. Программа\nкачества\nкогда команде не хватает сил", 330, 260, "r", 270, 130),
], edges=[E("hot", "bp"), E("bp", "lev"), E("lev", "vec"), E("vec", "mes"),
          E("mes", "team"), E("team", "prog")])

# own: three leverage points and how to test each
D["ch02-leverage-points"] = dict(items=[
    N("api", "Интерфейсы\nконтракт между системами", 0, 0, "p", 330, 100),
    N("state", "Stateful-системы\nсостояние труднее всего менять", 400, 0, "p", 330, 100),
    N("dm", "Модели данных\nстык интерфейса и состояния", 800, 0, "p", 330, 100),
    N("t_api", "Подключить ~6 клиентов\nк mock-реализации", 0, 200, "y", 330, 100),
    N("t_state", "Проверить отказы,\nсогласованность\nи бенчмарки как в проде", 400, 200, "y", 330, 100),
    N("t_dm", "Описать ~6 реальных\nсценариев", 800, 200, "y", 330, 100),
    N("spec", "Tech spec → обсуждение с командой и peers →\nслушать реальность и при реализации", 165, 400, "g", 800, 100),
], edges=[E("api", "t_api"), E("state", "t_state"), E("dm", "t_dm"),
          E("t_api", "spec"), E("t_state", "spec"), E("t_dm", "spec")])

if __name__ == "__main__":
    run_all(D)
