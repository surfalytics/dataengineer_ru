"""Проверка ch02_rocket_dag.py без сервера: разбор в DagBag и тестовый run через dag.test()."""
import contextlib
import io
import logging
import os
import tempfile
from pathlib import Path

os.environ.setdefault("AIRFLOW__CORE__LOAD_EXAMPLES", "False")
os.environ["ROCKET_DIR"] = tempfile.mkdtemp(prefix="rockets_")
folder = Path(__file__).resolve().parent
with contextlib.redirect_stdout(io.StringIO()):
    from airflow.dag_processing.dagbag import DagBag, sync_bag_to_db

    bag = DagBag(dag_folder=str(folder / "ch02_rocket_dag.py"))
    sync_bag_to_db(bag, "dags-folder", None)  # test() берёт DAG из БД сериализованным
    dag = bag.dags["rocket_launches"]
    logging.disable(logging.CRITICAL)
    run = dag.test()  # запускает tasks по порядку в одном процессе
print("ошибки импорта:", bag.import_errors or "нет")
print("порядок:", " >> ".join(t.task_id for t in dag.topological_sort()))
for ti in run.get_task_instances():
    print(f"{ti.task_id}: {ti.state}")
print("файлов в images:", len(list((Path(os.environ["ROCKET_DIR"]) / "images").iterdir())))
