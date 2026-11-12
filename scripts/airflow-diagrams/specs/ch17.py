from lib import N, E, Z, T
D = {}

D["ch17-deploy-choice"] = dict(items=[
    N("start", "Нужен Airflow\nв production", 350, 0, "n"),
    N("managed", "Managed сервис\nменьше работы", 0, 150, "g"),
    N("own", "Свой Kubernetes\nбольше контроля", 700, 150, "p"),
    N("astro", "Astronomer Astro\nлюбое облако", 0, 300, "g"),
    N("composer", "Google Cloud\nComposer (GKE)", 0, 450, "g"),
    N("mwaa", "Amazon MWAA\nDAG в S3", 0, 600, "g"),
    N("helm", "Official Helm Chart\nhelm upgrade --install", 700, 300, "p"),
    N("ext", "Внешний PostgreSQL\nсвой secret key", 700, 450, "db"),
    N("dags", "Выбрать способ\nдоставки DAG", 700, 600, "q"),
], edges=[
    E("start", "managed"),
    E("start", "own"),
    E("managed", "astro"),
    E("astro", "composer", head=False),
    E("composer", "mwaa", head=False),
    E("own", "helm"),
    E("helm", "ext"),
    E("ext", "dags"),
])

D["ch17-dag-delivery"] = dict(items=[
    N("image", "DAG внутри image\nCOPY в Dockerfile", 0, 0, "p"),
    N("pvc", "Persistent volume\nобщая папка", 350, 0, "y"),
    N("git", "Git-sync\nрепозиторий Git", 700, 0, "pu"),
    N("pods", "Pods Airflow\nscheduler, dag-processor,\nworker", 350, 200, "g"),
    T("immutable, версия ясна", 0, 120, 16),
    T("удобно для многих команд", 350, 120, 16),
    T("sync-контейнер тянет код", 700, 120, 16),
], edges=[
    E("image", "pods"),
    E("pvc", "pods"),
    E("git", "pods"),
])
