"""Глава 6: запуск двух DAG без сервера через dag.test() и вывод статусов tasks.
Нужен Airflow 3.4.0 (команда airflow рядом с python). БД: sqlite во временной папке."""
import contextlib
import io
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

folder = Path(__file__).resolve().parent
home = Path(tempfile.mkdtemp())
dags = home / "dags"
dags.mkdir()
for name in ("ch06_branch_dag.py", "ch06_trigger_rules_dag.py"):
    shutil.copy(folder / name, dags / name)
env = dict(os.environ, AIRFLOW_HOME=str(home), AIRFLOW__CORE__DAGS_FOLDER=str(dags),
           AIRFLOW__CORE__LOAD_EXAMPLES="False")
os.environ.update(env)
logging.disable(logging.CRITICAL)
airflow = str(Path(sys.executable).parent / "airflow")
for args in (("db", "migrate"), ("dags", "reserialize")):
    subprocess.run([airflow, *args], env=env, capture_output=True)

with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    from airflow.dag_processing.dagbag import DagBag

    bag = DagBag(dag_folder=str(dags))
print("ошибки импорта:", bag.import_errors or "нет")


def run(dag_id, date):
    when = datetime.fromisoformat(date).replace(tzinfo=timezone.utc)
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        dr = bag.dags[dag_id].test(logical_date=when)
    return {ti.task_id: str(ti.state) for ti in dr.get_task_instances()}


for date in ("2025-01-02", "2025-07-02"):
    states = run("umbrella_branch", date)
    print(f"umbrella_branch, logical_date {date}:")
    for t in ("pick_erp_system", "fetch_sales_old", "fetch_sales_new", "join_erp_branch", "join_datasets", "deploy_model"):
        print(f"  {t}: {states[t]}")

states = run("trigger_rules_demo", "2025-01-02")
print("trigger_rules_demo:")
for t in sorted(states):
    if t.startswith(("a_", "b_")):
        print(f"  {t}: {states[t]}")
shutil.rmtree(home, ignore_errors=True)
