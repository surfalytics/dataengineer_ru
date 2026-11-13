"""Глава 13: проверка без сервера. DagBag разбирает DAG проекта.
Запуск: $VENV/bin/python -I ch13_check.py"""
import contextlib
import io
import logging
from pathlib import Path

logging.disable(logging.CRITICAL)
from airflow.dag_processing.dagbag import DagBag  # noqa: E402

with contextlib.redirect_stdout(io.StringIO()):
    bag = DagBag(dag_folder=str(Path(__file__).resolve().parent / "ch13_nyc_dag.py"))
print("ошибки импорта:", bag.import_errors or "нет")
d = bag.dags["nyc_dag"]
print("tasks:", sorted(d.task_dict))
print("timetable:", type(d.timetable).__name__)
