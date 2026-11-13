"""Глава 12: проверка без сервера. DagBag разбирает DAG. Запуск mapping: airflow dags test (см. README-ch12.md).
Запуск: $VENV/bin/python -I ch12_check.py"""
import contextlib
import io
import logging
import sys
from pathlib import Path

logging.disable(logging.CRITICAL)
HERE = Path(__file__).resolve().parent

from airflow.dag_processing.dagbag import DagBag  # noqa: E402

with contextlib.redirect_stdout(io.StringIO()):
    bags = [DagBag(dag_folder=str(HERE / f)) for f in ("ch12_factory_dag.py", "ch12_mapping_dag.py")]
errors = {k: v for b in bags for k, v in b.import_errors.items()}
print("ошибки импорта:", errors or "нет")
dags = {k: v for b in bags for k, v in b.dags.items()}
for dag_id in ["factory_customers", "factory_sales", "grouped", "reviews_mapping"]:
    d = dags[dag_id]
    print(dag_id, "->", sorted(d.task_dict))
m = dags["reviews_mapping"]
print("print_rating mapped:", m.get_task("print_rating").is_mapped)
print("pool:", m.get_task("print_rating").pool)
print("timetable:", type(m.timetable).__name__)

sys.path.insert(0, str(HERE))
import ch12_light_task  # noqa: E402

print("call_api это task:", ch12_light_task.call_api.__class__.__name__)
