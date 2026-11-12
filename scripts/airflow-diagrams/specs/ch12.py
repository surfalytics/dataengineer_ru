from lib import N, E, Z, T
D = {}

D["ch12-parse-vs-run"] = dict(items=[
    Z("DAG processor: парсинг", 0, 0, 330, 570),
    Z("Worker: выполнение задачи", 450, 0, 330, 570),
    N("file", "Файл DAG\n(Python)", 40, 70, "n"),
    N("bad", "Плохо: тяжёлый код\nвне задач (БД, API)", 40, 300, "r"),
    N("good", "Хорошо: только\nописание задач", 40, 440, "g", h=90),
    N("task", "Задача читает\nconnection и config", 490, 70, "p"),
    N("heavy", "Тяжёлая работа:\nвычисления, запросы", 490, 220, "g"),
    N("ext", "Внешняя система\n(Spark, БД)", 490, 350, "db", h=90),
], edges=[
    E("file", "bad"), E("bad", "good", "лучше", dashed=True),
    E("task", "heavy"), E("heavy", "ext", "offload"),
])

D["ch12-dynamic-mapping"] = dict(items=[
    N("fetch", "fetch_ratings\nвернул N записей", 300, 0, "p"),
    N("exp", ".expand()\nпо списку", 300, 150, "y"),
    N("m0", "print_rating\n[0]", 0, 330, "g"),
    N("m1", "print_rating\n[1]", 300, 330, "g"),
    N("m2", "print_rating\n[N-1]", 600, 330, "g"),
    T("N меняется от запуска к запуску", 270, 470),
], edges=[
    E("fetch", "exp"), E("exp", "m0"), E("exp", "m1"), E("exp", "m2"),
])
