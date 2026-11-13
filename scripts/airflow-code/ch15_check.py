"""Глава 15: проверка без сервера. Значения по умолчанию из конфига, DagBag, callback при сбое.
Запуск: $VENV/bin/python -I scripts/airflow-code/ch15_check.py"""
import contextlib
import io
import logging
from pathlib import Path

logging.disable(logging.CRITICAL)
HERE = Path(__file__).resolve().parent

from airflow.configuration import conf  # noqa: E402
from airflow.dag_processing.dagbag import DagBag  # noqa: E402

print("значения по умолчанию в Airflow 3.4:")
for section, key in [
    ("core", "executor"),
    ("core", "parallelism"),
    ("core", "max_active_tasks_per_dag"),
    ("core", "max_active_runs_per_dag"),
    ("celery", "worker_concurrency"),
    ("dag_processor", "refresh_interval"),
    ("dag_processor", "parsing_processes"),
    ("scheduler", "job_heartbeat_sec"),
]:
    print(f"  {section}.{key} = {conf.get(section, key)}")

with contextlib.redirect_stdout(io.StringIO()):
    bag = DagBag(dag_folder=str(HERE / "ch15_callbacks_dag.py"))
print("ошибки разбора:", bag.import_errors or "нет")
dag = bag.dags["nightly_export"]
task = dag.task_dict["export"]
def names(cb):
    return [f.__name__ for f in (cb if isinstance(cb, list) else [cb])]


print("callback у DAG:", names(dag.on_failure_callback))
print("callback у task:", names(task.on_failure_callback))
print("executor у task:", task.executor)
