from lib import N, E, Z, T
D = {}
D["ch09-layers"] = dict(items=[
    N("dag", "DAG\n(только связи и параметры)", 275, 0, "p"),
    N("op", "Custom operator\nexecute()", 0, 150, "pu"),
    N("sn", "Custom sensor\npoke()", 550, 150, "pu"),
    N("hk", "Custom hook\nget_conn(), get_orders()", 275, 300, "y"),
    N("cn", "Airflow Connection\n(login, host, port)", 0, 450, "db"),
    N("api", "Внешний API\n(пагинация, auth)", 550, 450, "n"),
], edges=[
    E("dag", "op"), E("dag", "sn"),
    E("op", "hk"), E("sn", "hk"),
    E("hk", "cn", "conn_id"),
    E("hk", "api", "requests"),
])
D["ch09-deferrable"] = dict(items=[
    N("w1", "Worker:\nexecute() вызывает defer()", 0, 0, "p"),
    N("df", "Task = deferred\nworker slot свободен", 0, 150, "y"),
    N("tg", "Triggerer: async run()\nawait asyncio.sleep()", 0, 300, "pu"),
    N("ev", "TriggerEvent\nусловие выполнено", 0, 450, "g"),
    N("w2", "Worker:\nexecute_complete()", 0, 600, "p"),
    N("ok", "Scheduler:\ntask = success", 0, 750, "g"),
    N("ext", "Внешняя система\n(API, Spark, S3)", 400, 300, "n"),
    T("один triggerer ведёт\nсотни ожидающих tasks", 400, 420, 16),
], edges=[
    E("w1", "df"), E("df", "tg"), E("tg", "ev"), E("ev", "w2"), E("w2", "ok"),
    E("tg", "ext", "проверка", dashed=True),
])
