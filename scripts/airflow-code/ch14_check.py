"""Проверка DAG главы 14 без Docker: DagBag разбирает файл, порядок задач как в книге.
Запуск: $VENV/bin/python -I scripts/airflow-code/ch14_check.py"""
import contextlib
import io
from pathlib import Path

from airflow.dag_processing.dagbag import DagBag

HERE = Path(__file__).resolve().parent
with contextlib.redirect_stdout(io.StringIO()):
    bag = DagBag(dag_folder=str(HERE / "ch14_ingestion_dag.py"))
print("ошибки разбора:", bag.import_errors or "нет")
dag = bag.dags["ch14_ingestion"]
order = [t.task_id for t in dag.topological_sort()]
print("порядок:", " -> ".join(order))
print("команда compare:", dag.task_dict["compare_objects"].command)
