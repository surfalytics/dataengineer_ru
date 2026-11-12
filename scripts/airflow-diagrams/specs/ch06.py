from lib import N, E, Z, T
D = {}

D["ch06-branching"] = dict(items=[
    N("start", "start\n(EmptyOperator)", 0, 150, "n"),
    N("pick", "pick_source\nBranchPythonOperator", 350, 150, "y"),
    N("old", "load_old\n(старая ERP)", 700, 0, "p"),
    N("new", "load_new\n(новая ERP)", 700, 300, "p"),
    N("join", "join\ntrigger_rule=\nnone_failed", 1050, 150, "g"),
    N("pub", "publish", 1400, 150, "p"),
    T("Одна ветка выполняется,\nвторая получает skipped", 650, 440),
], edges=[
    E("start", "pick"),
    E("pick", "old", "return \"load_old\""),
    E("pick", "new", "return \"load_new\"", dashed=True),
    E("old", "join"),
    E("new", "join"),
    E("join", "pub"),
])

D["ch06-trigger-rules"] = dict(items=[
    N("up", "Upstream-задача\nupstream_failed / skipped", 0, 150, "r"),
    N("all", "all_success\n(по умолчанию)\nпропуск и сбой идут вниз", 400, 0, "n"),
    N("nf", "none_failed\nпропуск допустим,\nсбой идёт вниз", 400, 200, "g"),
    N("done", "all_done\nзапуск при любом статусе\n(cleanup)", 400, 400, "y"),
], edges=[
    E("up", "all"), E("up", "nf"), E("up", "done"),
])
