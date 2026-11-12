from lib import N, E, Z, T
D = {}

D["ch04-asset-flow"] = dict(items=[
    N("prod", "Producer DAG\nfetch_events\n(outlets=[asset])", 0, 150, "p"),
    N("asset", "Asset\nfile:///data/events", 350, 150, "db"),
    N("c1", "Consumer: analytics\nschedule=[asset]", 700, 0, "g"),
    N("c2", "Consumer: marketing\nschedule=[asset]", 700, 150, "g"),
    N("c3", "Consumer: monitoring\nschedule=[asset]", 700, 300, "g"),
], edges=[
    E("prod", "asset", "asset event"),
    E("asset", "c1", "запуск"),
    E("asset", "c2", "запуск"),
    E("asset", "c3", "запуск"),
])

D["ch04-multi-assets"] = dict(items=[
    N("p1", "Producer 1\nобновляет asset 1", 0, 0, "p"),
    N("p2", "Producer 2\nобновляет asset 2", 0, 200, "p"),
    N("a1", "Asset 1\nсобытие пришло", 350, 0, "db"),
    N("a2", "Asset 2\nсобытие пришло", 350, 200, "db"),
    N("cons", "Consumer DAG\nschedule=[a1, a2]\n(AND)", 700, 100, "g"),
    T("Запуск, когда оба asset\nполучили событие.\nПорядок не важен.", 700, 250),
], edges=[
    E("p1", "a1"), E("p2", "a2"),
    E("a1", "cons"), E("a2", "cons"),
])
