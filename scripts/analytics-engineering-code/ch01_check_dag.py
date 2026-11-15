"""Проверка ch01_simple_dag.py без сервера: разбор в DagBag и печать структуры DAG."""
import contextlib
import io
import logging
import os
from pathlib import Path

os.environ.setdefault("AIRFLOW__CORE__LOAD_EXAMPLES", "False")
logging.disable(logging.CRITICAL)

folder = Path(__file__).resolve().parent
with contextlib.redirect_stdout(io.StringIO()):  # Airflow пишет свой лог в stdout: прячем его
    try:
        from airflow.dag_processing.dagbag import DagBag
    except ImportError:
        from airflow.models.dagbag import DagBag
    bag = DagBag(dag_folder=str(folder / "ch01_simple_dag.py"), include_examples=False)
print("ошибки импорта:", bag.import_errors or "нет")
dag = bag.dags["hourly_demo"]
print("tasks:", " >> ".join(t.task_id for t in dag.topological_sort()))
print("расписание:", dag.schedule)
print("retries:", {t.task_id: t.retries for t in dag.tasks})
