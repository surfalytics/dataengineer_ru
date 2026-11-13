"""Глава 7: DagBag разбирает оба DAG без ошибок. Нужен Airflow и providers (Kafka, common-messaging)."""
import sys
from pathlib import Path

from airflow.models import DagBag

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here))
for name in ("ch07_sensor_dag.py", "ch07_kafka_dag.py"):
    bag = DagBag(dag_folder=str(here / name), safe_mode=False)
    for dag_id, dag in bag.dags.items():
        print(name, "->", dag_id, sorted(dag.task_dict))
    print("ошибки разбора:", bag.import_errors or "нет")
