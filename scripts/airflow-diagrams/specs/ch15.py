from lib import N, E, Z, T
D = {}

D["ch15-executors"] = dict(items=[
    N("sch", "Scheduler\n(task executor)", 450, 0, "p"),
    N("loc", "LocalExecutor\nподпроцессы на\nодной машине", 0, 170, "n"),
    N("cel", "CeleryExecutor\nочередь + workers\nна многих машинах", 300, 170, "p"),
    N("k8s", "KubernetesExecutor\nодин pod на task", 600, 170, "pu"),
    N("edge", "EdgeExecutor\nworker снаружи,\nсвязь через API", 900, 170, "y"),
    T("проще всего,\nпо умолчанию", 20, 300),
    T("нужен broker\n(Redis, RabbitMQ)", 320, 300),
    T("нужен кластер\nKubernetes", 620, 300),
    T("экспериментальный,\nдля особых сред", 920, 300),
], edges=[
    E("sch", "loc"), E("sch", "cel"), E("sch", "k8s"), E("sch", "edge"),
])

D["ch15-metrics-stack"] = dict(items=[
    N("af", "Airflow\nStatsD / OTel", 0, 0, "p"),
    N("ex", "StatsD exporter\nперевод формата", 350, 0, "pu"),
    N("pm", "Prometheus\nхранит метрики", 700, 0, "db"),
    N("gf", "Grafana\nдашборды", 1050, 0, "g"),
    N("al", "Alerts:\ncallback, email, Slack", 0, 200, "r"),
], edges=[
    E("af", "ex", "push"), E("ex", "pm", "pull"), E("pm", "gf", "query"), E("af", "al", "on_failure_callback"),
])
