"""Глава 2: что видно при сбое. Task get_pictures падает, notify получает upstream_failed.
Запускаем ch02_failure_dag.py через dag.test() и печатаем статусы tasks."""
import contextlib
import io
import logging
import os
from pathlib import Path

os.environ.setdefault("AIRFLOW__CORE__LOAD_EXAMPLES", "False")
logging.disable(logging.CRITICAL)
folder = Path(__file__).resolve().parent
with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    from airflow.dag_processing.dagbag import DagBag, sync_bag_to_db

    bag = DagBag(dag_folder=str(folder / "ch02_failure_dag.py"))
    sync_bag_to_db(bag, "dags-folder", None)  # test() берёт DAG из БД сериализованным
    try:
        run = bag.dags["rocket_failure"].test()
    except Exception as e:  # noqa: BLE001
        raise SystemExit(f"dag.test() упал: {e!r}")
for ti in run.get_task_instances():
    print(f"{ti.task_id}: {ti.state}")
