"""Глава 17: проверка DAG без кластера. DagBag читает файл и показывает executor и image каждой task.
Запуск: $VENV/bin/python -I ch17_check_executor_dag.py"""
import contextlib
import io
import logging
import os
from pathlib import Path

# Так задаётся executor в настройках Airflow. Helm values делает то же самое
os.environ["AIRFLOW__CORE__EXECUTOR"] = "CeleryExecutor,KubernetesExecutor"
logging.disable(logging.CRITICAL)
HERE = Path(__file__).resolve().parent

from airflow.dag_processing.dagbag import DagBag  # noqa: E402

with contextlib.redirect_stdout(io.StringIO()):
    bag = DagBag(dag_folder=str(HERE / "ch17_multi_executor_dag.py"))
print("ошибки импорта:", bag.import_errors or "нет")
dag = bag.dags["executors_demo"]
for task_id in sorted(dag.task_dict):
    t = dag.task_dict[task_id]
    image = "по умолчанию"
    if t.executor_config:
        image = t.executor_config["pod_override"].spec.containers[0].image
    print(f"{task_id}: executor={t.executor}, image={image}")
