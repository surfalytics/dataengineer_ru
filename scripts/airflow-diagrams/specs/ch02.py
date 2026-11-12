from lib import N, E, Z, T

D = {}

D["ch02-rocket-dag"] = dict(items=[
    N("api", "Launch Library API", 0, 0, "n"),
    N("dl", "download_launches\nBashOperator", 0, 150, "p"),
    N("gp", "get_pictures\nPythonOperator", 0, 300, "p"),
    N("nt", "notify\nBashOperator", 0, 450, "p"),
    N("json", "/tmp/launches.json", 350, 150, "db"),
    N("img", "/tmp/images", 350, 300, "db"),
], edges=[
    E("api", "dl", "curl"),
    E("dl", "gp", ">>"),
    E("gp", "nt", ">>"),
    E("dl", "json", "пишет"),
    E("json", "gp", "читает", dashed=True),
    E("gp", "img", "пишет"),
])

D["ch02-failure-clear"] = dict(items=[
    N("fail", "get_pictures\nfailed", 0, 0, "r"),
    N("up", "notify\nupstream_failed", 0, 150, "q"),
    N("clear", "Clear Task Instance\n+ Downstream", 500, 75, "y"),
    N("rerun", "get_pictures и notify\nзапускаются снова", 1000, 75, "g"),
], edges=[
    E("fail", "up", "notify не стартует"),
    E("fail", "clear", "чиним причину"),
    E("clear", "rerun"),
])
