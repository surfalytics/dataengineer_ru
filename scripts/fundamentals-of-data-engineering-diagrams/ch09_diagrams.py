#!/usr/bin/env python3
"""Chapter 9 (serving data) diagrams. Usage: ch09_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

# Fig 9-1 (main): serving delivers data for three use cases
D["ch09-use-cases"] = dict(items=[
    N("src", "Обработанные данные\n(warehouse, lake)\nэтап serving", 0, 230, "db", 340, 160),
    N("a", "Аналитика и BI\nдашборды, отчёты,\nad hoc анализ", 640, 0, "p", 360, 130),
    N("m", "ML\nобучение моделей,\nфичи для data scientists", 640, 215, "g", 360, 130),
    N("r", "Reverse ETL\nвозврат данных\nв рабочие системы", 640, 430, "y", 360, 130),
    N("crm", "Рабочие системы\n(CRM, ad tech)", 1300, 430, "n", 320, 130),
    N("base", "Общая основа для всех трёх: доверие к данным, SLA и SLO, единые определения метрик, безопасность", 0, 680, "pu", 1620, 100),
], edges=[E("src", "a"), E("src", "m"), E("src", "r"), E("r", "crm", "обратно в источник")])

# own: ways to serve data for analytics and ML
rows = [
    ("File exchange\nфайлы, object storage", "Потребитель не умеет иначе. Файл по почте = много версий, доступ не отозвать", "n"),
    ("База (OLAP)", "Нужны схема, права на таблицы, строки и колонки, скорость и concurrency", "p"),
    ("Streaming и\noperational DB", "Нужны история и свежие данные в одном запросе", "db"),
    ("Query federation", "Ad hoc анализ без копирования, источник под контролем", "g"),
    ("Data sharing", "Обмен между командами и компаниями в облаке: задача доступа", "y"),
    ("Semantic и\nmetrics layer", "Бизнес-логика один раз, поверх любого из способов выше", "pu"),
]
items, edges = [], []
for i, (l, r, k) in enumerate(rows):
    y = i * 150
    items += [N(f"l{i}", l, 0, y, k, 380, 110), N(f"r{i}", r, 560, y, "n", 760, 110)]
    edges.append(E(f"l{i}", f"r{i}", "когда"))
D["ch09-ways-to-serve"] = dict(items=items, edges=edges)

# Fig 9-3: federated query with three sources
D["ch09-federation"] = dict(items=[
    N("u", "Аналитик\nad hoc запрос", 0, 190, "p", 280, 130),
    N("eng", "Движок federation\nTrino, Presto,\nStarburst", 460, 175, "g", 340, 160),
    N("s1", "OLTP-база\n(живая система)", 980, 0, "db", 340, 110),
    N("s2", "OLAP / warehouse", 980, 200, "db", 340, 110),
    N("s3", "Файлы, API,\nobject storage", 980, 400, "db", 340, 110),
    N("note", "Данные не копируются: запрос идёт прямо в источники. Следите за нагрузкой на живые системы.", 0, 600, "y", 1320, 90),
], edges=[E("u", "eng", "один SQL"), E("eng", "s1"), E("eng", "s2"), E("eng", "s3")])

# Fig 9-4 + own: notebook sources and how to grow out of laptop memory
items = [N(f"s{i}", t, i * 340, 0, "db", 300, 100) for i, t in enumerate(
    ["API", "База данных", "Warehouse", "Object storage,\nlake"])]
items += [
    N("nb", "Notebook data scientist\n(Jupyter, pandas), данные в памяти", 330, 210, "p", 660, 110),
    T("Данные не влезли в память? Двигайтесь вправо:", 0, 400, 22, "#495057"),
    N("l1", "Облачный notebook\nпамять и диск растут", 0, 460, "g", 300, 130),
    N("l2", "Распределённые\nсистемы: Dask,\nRay, Spark", 340, 460, "g", 300, 130),
    N("l3", "Облачные платформы ML:\nSageMaker, Vertex AI,\nAzure ML", 680, 460, "g", 300, 130),
    N("l4", "Open source:\nKubeflow, MLflow", 1020, 460, "g", 300, 130),
]
edges = [E(f"s{i}", "nb") for i in range(4)] + [E("l1", "l2"), E("l2", "l3"), E("l3", "l4")]
D["ch09-notebooks"] = dict(items=items, edges=edges)

# Fig 9-5: reverse ETL on the lead scoring example, with the feedback-loop risk
D["ch09-reverse-etl"] = dict(items=[
    N("crm", "CRM\nрабочая система:\nклиенты, заказы,\nпродавцы", 0, 0, "n", 300, 410),
    N("w", "Warehouse\nданные клиентов\nи заказов", 540, 0, "db", 300, 120),
    N("mod", "Модель\nlead scoring", 1080, 0, "g", 300, 120),
    N("sc", "Warehouse\nоценки лидов", 1080, 290, "db", 300, 120),
    N("re", "Reverse ETL\nзагрузка в CRM", 540, 290, "y", 300, 120),
    N("risk", "Риск: feedback loop. Ошибка модели ставок поднимает ставки, клики растут, деньги уходят. Нужны мониторинг и лимиты.", 0, 520, "r", 1380, 100),
], edges=[E("crm", "w", "ingestion"), E("w", "mod", "обучение"), E("mod", "sc", "оценки"),
          E("sc", "re", "выгрузка"), E("re", "crm", "оценки в CRM")])

if __name__ == "__main__":
    run_all(D)
