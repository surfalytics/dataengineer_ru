"""Проверка ch01_weather_dag.py без запущенного сервера: разбор в DagBag.
Тестовый run: airflow dags test weather_board 2026-01-02 (см. README-ch01.md)."""
import contextlib
import io
import logging
import os
from pathlib import Path

os.environ.setdefault("AIRFLOW__CORE__LOAD_EXAMPLES", "False")
logging.disable(logging.CRITICAL)

folder = Path(__file__).resolve().parent
with contextlib.redirect_stdout(io.StringIO()):  # Airflow пишет свой лог в stdout: прячем его
    from airflow.dag_processing.dagbag import DagBag

    bag = DagBag(dag_folder=str(folder / "ch01_weather_dag.py"))
print("ошибки импорта:", bag.import_errors or "нет")
dag = bag.dags["weather_board"]
print("tasks:", sorted(t.task_id for t in dag.tasks))
print("цепочка:", " >> ".join(t.task_id for t in dag.topological_sort()))
print("retries у fetch:", dag.get_task("fetch").retries)
print("расписание:", dag.schedule)
