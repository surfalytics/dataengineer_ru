"""Глава 15: что Airflow шлёт в StatsD. Свой UDP-сервер ловит пакеты (вместо statsd-exporter).
Нужен пакет statsd (extra apache-airflow[statsd]). Если пакета нет в окружении, путь к нему в CH15_SITE."""
import logging
import os
import socket
import sys

if os.environ.get("CH15_SITE"):
    sys.path.insert(0, os.environ["CH15_SITE"])
logging.disable(logging.CRITICAL)

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP, как у StatsD
server.bind(("127.0.0.1", 0))  # свободный порт, чтобы не мешать другим программам
server.settimeout(2)

# настройки до импорта Airflow: включаем StatsD и указываем наш порт
os.environ["AIRFLOW__METRICS__STATSD_ON"] = "True"
os.environ["AIRFLOW__METRICS__STATSD_HOST"] = "127.0.0.1"
os.environ["AIRFLOW__METRICS__STATSD_PORT"] = str(server.getsockname()[1])
os.environ["AIRFLOW__METRICS__STATSD_PREFIX"] = "airflow"

from airflow.configuration import conf  # noqa: E402
from airflow._shared.observability.metrics import stats  # noqa: E402
from airflow.observability.metrics import stats_utils  # noqa: E402

# так Airflow сам включает отправку метрик (см. executors/base_executor.py)
stats.initialize(
    factory=stats_utils.get_stats_factory(),
    export_legacy_names=conf.getboolean("metrics", "legacy_names_on"),
)
stats.incr("ti_failures")  # одна упавшая task
stats.gauge("executor.open_slots", 28)  # свободные слоты executor
stats.gauge("dag_processing.import_errors", 0)  # ошибок разбора DAG нет

for _ in range(3):
    data, _addr = server.recvfrom(1024)
    print(data.decode())
