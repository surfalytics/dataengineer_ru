from lib import N, E, Z, T
D = {}

D["ch11-container-workflow"] = dict(items=[
    N("dev", "Разработчик:\nDockerfile + скрипт", 0, 0, "n"),
    N("build", "docker build\n(локально или CI)", 0, 150, "p"),
    N("reg", "Image registry", 0, 300, "db"),
    N("dag", "DAG с\nDockerOperator", 350, 0, "p"),
    N("worker", "Airflow worker", 350, 150, "p"),
    N("pull", "Pull image\nиз registry", 350, 300, "pu"),
    N("cont", "Контейнер задачи:\nдепенденси внутри", 350, 450, "g"),
    N("vol", "Volume с данными", 900, 450, "db"),
], edges=[
    E("dev", "build"), E("build", "reg", "push"),
    E("dag", "worker", "запуск задачи"), E("worker", "pull"),
    E("reg", "pull", dashed=True), E("pull", "cont"),
    E("cont", "vol", "читает и пишет"),
])

D["ch11-docker-vs-k8s"] = dict(items=[
    Z("Docker", 0, 0, 330, 520),
    Z("Kubernetes", 450, 0, 330, 520),
    N("w1", "Airflow worker", 40, 70, "p"),
    N("d1", "Docker daemon\nна том же хосте", 40, 220, "pu"),
    N("c1", "Контейнер задачи", 40, 370, "g"),
    N("w2", "Airflow worker", 490, 70, "p"),
    N("api", "Kubernetes API\n+ scheduler", 490, 220, "pu"),
    N("pod", "Pod на отдельном\nnode", 490, 370, "g"),
], edges=[
    E("w1", "d1", "docker run"), E("d1", "c1"),
    E("w2", "api", "создать pod"), E("api", "pod"),
])
