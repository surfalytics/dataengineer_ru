from lib import N, E, Z, T
D = {}

D["ch10-ci-pipeline"] = dict(items=[
    N("push", "git push\nв репозиторий", 0, 0, "n"),
    N("lint", "Static checks\nRuff / Flake8 / Black", 0, 150, "p"),
    N("integrity", "DAG integrity test\nDagBag + pytest", 0, 300, "p"),
    N("unit", "Unit tests\nexecute() + mock", 0, 450, "p"),
    N("integ", "Integration tests\nDocker-контейнеры", 0, 600, "pu"),
    N("ok", "Всё зелёное:\nmerge и deploy", 0, 750, "g"),
    N("fail", "Ошибка:\nmerge заблокирован", 350, 300, "r"),
    T("Каждый шаг ловит свой тип ошибок", 330, 450),
], edges=[
    E("push", "lint"), E("lint", "integrity"), E("integrity", "unit"),
    E("unit", "integ"), E("integ", "ok"),
    E("integrity", "fail", "падает", dashed=True),
])

D["ch10-mock-or-docker"] = dict(items=[
    N("task", "Оператор ходит\nво внешнюю систему", 300, 0, "p"),
    N("q", "Что вместо\nреальной системы?", 300, 150, "y", shape="diamond", h=120),
    N("mock", "Mock\nmocker.patch.object", 0, 350, "g"),
    N("docker", "Контейнер\npytest-docker-tools", 600, 350, "pu"),
    N("mockpro", "Быстро, без Docker.\nНужно знать, что вернёт\nсистема", 0, 500, "n"),
    N("dockerpro", "Реальные hooks.\nМедленнее, нужен Docker", 600, 500, "n"),
], edges=[
    E("task", "q"), E("q", "mock", "простой ответ"), E("q", "docker", "реальный SQL"),
    E("mock", "mockpro", head=False, dashed=True), E("docker", "dockerpro", head=False, dashed=True),
])
