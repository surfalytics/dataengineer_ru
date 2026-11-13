"""Проверка ch04_asset_dags.py без сервера: DagBag, затем тестовый запуск producer.
Нужен Airflow 3.4.0 (команда airflow рядом с python). БД: sqlite во временной папке."""
import contextlib
import io
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

logging.disable(logging.CRITICAL)
src = Path(__file__).resolve().parent / "ch04_asset_dags.py"
home = Path(tempfile.mkdtemp())
dags = home / "dags"
dags.mkdir()
shutil.copy(src, dags / src.name)
env = dict(os.environ, AIRFLOW_HOME=str(home), AIRFLOW__CORE__DAGS_FOLDER=str(dags),
           AIRFLOW__CORE__LOAD_EXAMPLES="False")
os.environ.update(env)
airflow = str(Path(sys.executable).parent / "airflow")


def cli(*args):
    return subprocess.run([airflow, *args], env=env, capture_output=True, text=True)


cli("db", "migrate")
cli("dags", "reserialize")
with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    from airflow.dag_processing.dagbag import DagBag

    bag = DagBag(dag_folder=str(dags / src.name))
print("ошибки импорта:", bag.import_errors or "нет")
for dag_id in sorted(bag.dags):
    sch = bag.dags[dag_id].schedule
    print(dag_id, "->", [a.uri for a in sch] if isinstance(sch, list) else sch)
r = cli("dags", "test", "orders_producer", "2025-01-02")
print("dags test producer:", "state=success" if "state=success" in r.stdout + r.stderr else "ошибка")
cli("dags", "test", "payments_producer", "2025-01-02")
from airflow.models.asset import AssetEvent
from airflow.utils.session import create_session

with create_session() as s:
    for ev in s.query(AssetEvent).order_by(AssetEvent.id):
        print("asset event:", ev.asset.uri, ev.extra)
    n = s.query(AssetEvent).count()
    print("всего событий:", n, "(payments пропущен, события нет)")
shutil.rmtree(home, ignore_errors=True)
