"""Глава 16: DAG из примера разбирается без ошибок. Запуск: $VENV/bin/python -I scripts/airflow-code/ch16_check.py"""
import contextlib
import io
import logging
from pathlib import Path

logging.disable(logging.CRITICAL)
from airflow.dag_processing.dagbag import DagBag  # noqa: E402

with contextlib.redirect_stdout(io.StringIO()):
    bag = DagBag(dag_folder=str(Path(__file__).resolve().parent / "ch16_partner_dag.py"))
print("ошибки разбора:", bag.import_errors or "нет")
task = bag.dags["call_partner_api"].task_dict["ping"]
print("conn_id в DAG:", task.http_conn_id)
