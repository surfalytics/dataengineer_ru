from lib import N, E, Z, T
D = {}

D["ch13-nyc-pipeline"] = dict(items=[
    N("citi", "Citi Bike\nREST API", 0, 0, "n"),
    N("taxi", "Yellow Cab\nfile share (CSV)", 300, 0, "n"),
    N("dl_citi", "download_\ncitibike_data", 0, 150, "p"),
    N("dl_taxi", "download_\ntaxi_data", 300, 150, "p"),
    N("raw", "MinIO: raw/\nсырые файлы", 150, 300, "db"),
    N("pandas", "PandasOperator\nрасчёт и очистка", 150, 450, "pu"),
    N("proc", "MinIO: processed/\nParquet", 150, 600, "db"),
    N("pg", "PostgreSQL\nрезультат", 150, 750, "db"),
    N("web", "Веб-страница\nтакси или bike?", 150, 900, "g"),
    T("DAG по расписанию */15", 620, 190),
], edges=[
    E("citi", "dl_citi"), E("taxi", "dl_taxi"),
    E("dl_citi", "raw"), E("dl_taxi", "raw"),
    E("raw", "pandas"), E("pandas", "proc"),
    E("proc", "pg"), E("pg", "web"),
])

D["ch13-idempotent-write"] = dict(items=[
    Z("Без защиты", 0, 0, 330, 520),
    Z("Идемпотентная запись", 400, 0, 330, 520),
    N("a1", "Task пишет\nappend в таблицу", 40, 70, "p"),
    N("a2", "Повторный запуск\n(retry, backfill)", 40, 220, "y"),
    N("a3", "Дубли строк\nв результате", 40, 370, "r"),
    N("b1", "Строки с колонкой\nrun = data_interval_start", 440, 70, "p"),
    N("b2", "Транзакция:\nDELETE этого run,\nпотом INSERT", 440, 220, "pu"),
    N("b3", "Повтор даёт тот\nже результат", 440, 370, "g"),
], edges=[
    E("a1", "a2"), E("a2", "a3"),
    E("b1", "b2"), E("b2", "b3"),
])
