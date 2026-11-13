"""Глава 8: проверка DAG mnist_train через DagBag и имён training job.
Без AWS. Запуск: python3 -I ch08_check_dag.py (нужны Airflow 3.4.0 и provider amazon)."""
import contextlib
import io
import logging
import os
from pathlib import Path

os.environ.setdefault("AIRFLOW__CORE__LOAD_EXAMPLES", "False")
logging.disable(logging.CRITICAL)

import pendulum  # noqa: E402

folder = Path(__file__).resolve().parent
with contextlib.redirect_stdout(io.StringIO()):  # Airflow пишет свой лог в stdout: прячем его
    from airflow.dag_processing.dagbag import DagBag

    bag = DagBag(dag_folder=str(folder / "ch08_sagemaker_dag.py"))
print("ошибки импорта:", bag.import_errors or "нет")
dag = bag.dags["mnist_train"]
train = dag.get_task("sagemaker_train_model")
print("tasks:", sorted(t.task_id for t in dag.tasks))
print("тип train:", type(train).__name__)
print("wait_for_completion:", train.wait_for_completion, "| check_interval:", train.check_interval)
print("config в template_fields:", "config" in train.template_fields)

# ts_nodash в Airflow: дата и время без разделителей, например 20250101T000000.
for d in ("2025-01-01", "2025-01-08"):
    ts = pendulum.parse(d).strftime("%Y%m%dT%H%M%S")
    print(f"logical_date {d} -> mnistclassifier-{ts}")
