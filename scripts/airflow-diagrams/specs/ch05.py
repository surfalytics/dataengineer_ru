from lib import N, E, Z, T
D = {}

D["ch05-context-flow"] = dict(items=[
    N("run", "Запуск задачи\n(DAG run)", 0, 150, "n"),
    N("ctx", "context\nlogical_date,\ndata_interval_*, run_id", 350, 150, "y"),
    N("bash", "BashOperator\nbash_command:\n{{ ds_nodash }}", 700, 0, "p"),
    N("py", "PythonOperator\nfunc(data_interval_start,\n**context)", 700, 300, "p"),
    N("r1", "Jinja подставляет\nзначения в строку", 1050, 0, "pu"),
    N("r2", "Airflow передаёт\nзначения в функцию", 1050, 300, "pu"),
], edges=[
    E("run", "ctx"),
    E("ctx", "bash", "template_fields"),
    E("ctx", "py", "keyword-аргументы"),
    E("bash", "r1"),
    E("py", "r2"),
])
