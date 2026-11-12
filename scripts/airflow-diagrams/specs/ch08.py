from lib import N, E, Z, T
D = {}
D["ch08-ml-pipeline"] = dict(items=[
    Z("Airflow DAG (offline, по расписанию)", 0, 0, 350, 780),
    N("b", "S3CreateBucket\n+ bucket policy", 50, 60, "p"),
    N("cp", "S3CopyObject\n(данные в свой bucket)", 50, 210, "p"),
    N("tr", "PythonOperator\n+ S3Hook (recordIO)", 50, 360, "pu"),
    N("tn", "SageMakerTraining\nOperator", 50, 510, "pu"),
    N("dp", "SageMakerEndpoint\nOperator", 50, 660, "pu", h=100),
    Z("Разовый деплой (CI/CD)", 500, 0, 350, 400),
    N("ep", "SageMaker\nendpoint", 550, 60, "db"),
    N("api", "Lambda +\nAPI Gateway", 550, 210, "n"),
    N("u", "Пользователь\nпосылает картинку", 550, 520, "g"),
], edges=[
    E("b", "cp"), E("cp", "tr"), E("tr", "tn"), E("tn", "dp"),
    E("dp", "ep", "модель"),
    E("api", "ep", "invoke", dashed=True),
    E("u", "api", "HTTP POST"),
])
D["ch08-a-to-b"] = dict(items=[
    N("a", "Система A\n(PostgreSQL)", 0, 0, "db"),
    N("ha", "PostgresHook\nget_records()", 0, 150, "pu"),
    N("op", "A-to-B operator\nexecute()", 300, 150, "p"),
    N("mid", "CSV в памяти\n(io.StringIO)", 300, 300, "y"),
    N("hb", "S3Hook\nload_file_obj()", 600, 150, "pu"),
    N("b", "Система B\n(S3 / MinIO)", 600, 0, "db"),
    T("replace=True: повтор\nбезопасен", 600, 280, 16),
], edges=[
    E("a", "ha", "connection ID"),
    E("ha", "op"),
    E("op", "mid"),
    E("mid", "hb"),
    E("hb", "b"),
])
