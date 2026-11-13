#!/usr/bin/env python3
"""Chapter 9 (real-world conversations and case studies) diagrams. Usage: ch09_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# main: four elements of a data mesh (Dehghani) + what it is not
D["ch09-mesh-four-elements"] = dict(items=[
    N("top", "Data mesh = сдвиг в организации и в технике (socio-technical shift)", 0, 0, "pu", 1400, 80),
    N("a", "1. Владение\nу доменов", 0, 170, "p", 320, 100),
    N("b", "2. Долгая\nответственность", 360, 170, "p", 320, 100),
    N("c", "3. Self-serve\nплатформа", 720, 170, "p", 320, 100),
    N("d", "4. Federated\ngovernance", 1080, 170, "p", 320, 100),
    N("a2", "Данными управляют\nлюди из бизнес-доменов,\nгде данные рождаются", 0, 340, "g", 320, 130),
    N("b2", "Команда думает как\nпродакт-менеджер:\ndata as a product", 360, 340, "g", 320, 130),
    N("c2", "Платформа прячет\nтехнику: хранение,\nпайплайны, каталог", 720, 340, "g", 320, 130),
    N("d2", "Общие правила:\nформат, метаданные,\nSLA и качество", 1080, 340, "g", 320, 130),
    N("not", "Это не data mesh: одно хранилище, один BI-инструмент,\nвиртуализация поверх баз микросервисов", 0, 560, "r", 1400, 100),
], edges=[E("top", "a"), E("top", "b"), E("top", "c"), E("top", "d"),
          E("a", "a2"), E("b", "b2"), E("c", "c2"), E("d", "d2")])

# own: Kolibri Games timeline 2016-2021 (merges Figures 9-2 .. 9-12)
cols = [
    ("2016", "Основатели\nв студенческой\nквартире", "Facebook Analytics,\nFirebase,\nGameAnalytics,\nad partners", "Аналитика\nразбросана,\nKPI непрозрачны"),
    ("2017", "Один\nмаркетолог", "+ AppsFlyer,\nлокальные скрипты\nдля ставок", "Нет version\ncontrol, данные\nещё разбросаннее"),
    ("2018", "Два data\nengineer и\nмаркетолог", "Azure, SQL database,\nPower BI → Looker", "SQL database\nтормозит, jobs\nпадают, мало alerts"),
    ("2019", "+ head of game\ndata и два\nBI developer", "Databricks,\nSnowflake, Looker", "A/B тесты неудобны,\nрешения по\nинтуиции"),
    ("2020", "9 человек,\nаналитики в\nпродуктовых командах", "Snowflake (ELT),\ndbt, Airflow", "Data trust,\nстабильность,\nмасштаб персонализации"),
    ("2021", "Домены с product\nи marketing +\nцентральная платформа", "+ data observability,\nобщий release\nprocess", "Цель: надёжные\nданные и data mesh"),
]
items, edges = [T("Команда", -230, 50, 20, "#495057"), T("Стек", -230, 245, 20, "#495057"), T("Проблема", -230, 450, 20, "#495057")], []
for i, (yr, team, stack, pain) in enumerate(cols):
    x = i * 310
    items += [N(f"t{i}", f"{yr}\n{team}", x, 0, "n" if i < 5 else "g", 270, 160),
              N(f"s{i}", stack, x, 200, "p", 270, 170),
              N(f"p{i}", pain, x, 410, "r" if i < 5 else "g", 270, 140)]
    edges += [E(f"t{i}", f"s{i}", dashed=True), E(f"s{i}", f"p{i}", dashed=True)]
    if i: edges.append(E(f"t{i-1}", f"t{i}"))
D["ch09-kolibri-timeline"] = dict(items=items, edges=edges)

# own: traditional catalog vs data discovery
rows = [
    ("Заполняют люди\nвручную", "Автоматизация:\nlineage на уровне\nтаблиц и полей (ML)"),
    ("Показывает идеальное,\n«каталожное»\nсостояние", "Показывает состояние\nпрямо сейчас:\nсвежесть, устаревшее"),
    ("Рассчитан на\nструктурные данные\nхранилища", "Работает в озере:\nJSON, Parquet,\nразные движки"),
    ("Интерфейс\nдля людей (UI)", "API для инженеров\nи self-service\nдля доменов"),
    ("Нет единого\nисточника истины\nо чтении и записи", "Источник истины,\nвидно, что нужно,\nа что не используют"),
]
items, edges = [T("Традиционный data catalog", 40, -50, 22, "#e03131"), T("Data discovery (federated catalog)", 640, -50, 22, "#2f9e44")], []
for i, (l, r) in enumerate(rows):
    y = i * 150
    items += [N(f"l{i}", l, 0, y, "r", 400, 120), N(f"r{i}", r, 600, y, "g", 440, 120)]
    edges.append(E(f"l{i}", f"r{i}"))
D["ch09-catalog-vs-discovery"] = dict(items=items, edges=edges)

# own: seven signals that it is time to invest in data quality
sig = [
    "Недавно переехали в облако",
    "Растут источники и таблицы\n(ориентир: больше 50 таблиц)",
    "Растёт команда данных",
    "30-50% времени уходит\nна тушение проблем",
    "Потребителей данных больше,\nчем год назад",
    "Переход на self-service\nаналитику",
    "Данные входят в продукт\nдля клиентов",
]
items, edges = [], []
for i, s in enumerate(sig):
    col, row = i % 3, i // 3
    items.append(N(f"s{i}", s, col * 420, row * 130, "y", 380, 100))
items.append(N("go", "Чем больше сигналов у вас совпало, тем раньше пора вкладываться в data quality", 0, 410, "g", 1220, 90))
D["ch09-start-signals"] = dict(items=items, edges=edges)

if __name__ == "__main__":
    run_all(D)
