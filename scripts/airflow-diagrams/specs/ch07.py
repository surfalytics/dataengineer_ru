from lib import N, E, Z, T
D = {}
D["ch07-triggers"] = dict(items=[
    N("s", "Sensor\n(опрос условия)", 0, 0, "y"),
    N("c", "CLI\nairflow dags trigger", 300, 0, "n"),
    N("a", "REST API\nPOST dagRuns", 600, 0, "n"),
    N("q", "Сообщение\nв очереди (Kafka)", 900, 0, "q"),
    N("w", "AssetWatcher +\nMessageQueueTrigger", 900, 150, "pu"),
    N("dag", "DAG run\nзапущен", 450, 330, "g"),
    N("t", "tasks читают\ndag_run.conf", 450, 480, "p"),
    N("tr", "triggerer\n(deferrable, asyncio)", 0, 150, "pu"),
    T("sensor: mode=reschedule\nосвобождает worker slot", 0, 270, 16),
], edges=[
    E("s", "tr", "defer", dashed=True),
    E("s", "dag", "условие True"),
    E("c", "dag", "conf"),
    E("a", "dag", "conf"),
    E("q", "w"),
    E("w", "dag", "Asset обновлён"),
    E("dag", "t"),
])
