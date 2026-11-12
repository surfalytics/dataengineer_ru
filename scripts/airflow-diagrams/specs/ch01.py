from lib import N, E, Z, T

D = {}

D["ch01-airflow-components"] = dict(items=[
    N("files", "DAG-файлы\n(папка dags)", 0, 0, "n"),
    N("proc", "DAG processor\nпарсит файлы", 0, 170, "pu"),
    N("api", "API server\nUI и шлюз к базе", 450, 170, "p"),
    N("user", "Пользователь\n(веб-интерфейс)", 900, 170, "n"),
    N("db", "Metastore\n(база метаданных)", 450, 340, "db"),
    N("sched", "Scheduler\nпланирует tasks", 0, 450, "y"),
    N("trig", "Triggerer\nждёт события", 900, 450, "pu"),
    N("work", "Workers\nвыполняют tasks", 450, 510, "g"),
], edges=[
    E("files", "proc"),
    E("proc", "api", "serialized DAG"),
    E("user", "api", "смотрит runs"),
    E("api", "db"),
    E("sched", "db", "DAG runs"),
    E("trig", "db", "deferred tasks"),
    E("sched", "work", "очередь tasks"),
    E("work", "db", "результаты"),
])

D["ch01-umbrella-dag"] = dict(items=[
    N("fw", "fetch_weather", 0, 0, "p"),
    N("cw", "clean_weather", 300, 0, "p"),
    N("fs", "fetch_sales", 0, 150, "p"),
    N("cs", "clean_sales", 300, 150, "p"),
    N("join", "join_datasets", 600, 75, "pu"),
    N("train", "train_model", 600, 225, "pu"),
    N("dep", "deploy_model", 600, 375, "g"),
    T("Две ветки независимы: идут параллельно", 0, 280),
], edges=[
    E("fw", "cw"), E("fs", "cs"), E("cw", "join"), E("cs", "join"),
    E("join", "train"), E("train", "dep"),
])
