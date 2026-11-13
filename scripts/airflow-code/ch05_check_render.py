"""Проверка ch05_stocksense_dag.py без сервера: DagBag + `airflow tasks render` для любой даты.
Нужен Airflow (см. README-ch05.md). AIRFLOW_HOME берётся из окружения."""
import contextlib
import io
import logging
import os
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("AIRFLOW__CORE__LOAD_EXAMPLES", "False")
logging.disable(logging.CRITICAL)
folder = Path(__file__).resolve().parent
os.environ["AIRFLOW__CORE__DAGS_FOLDER"] = str(folder / "_dags_ch05")

with contextlib.redirect_stdout(io.StringIO()):
    from airflow.dag_processing.dagbag import DagBag

    bag = DagBag(dag_folder=str(folder / "ch05_stocksense_dag.py"))
print("ошибки импорта:", bag.import_errors or "нет")
dag = bag.dags["stocksense_templating"]
print("tasks:", " >> ".join(t.task_id for t in dag.topological_sort()))
for t in dag.tasks:
    print(f"template_fields у {t.task_id}: {list(t.template_fields)[:3]}")

import shutil
shutil.rmtree(folder / "_dags_ch05", ignore_errors=True)
(folder / "_dags_ch05").mkdir()
shutil.copy(folder / "ch05_stocksense_dag.py", folder / "_dags_ch05")
airflow = str(Path(sys.executable).parent / "airflow")
for task in ("show_name", "get_data"):
    r = subprocess.run([airflow, "tasks", "render", "stocksense_templating", task, "2025-04-24T22:00:00"],
                       capture_output=True, text=True, env=os.environ)
    lines = [l for l in r.stdout.splitlines() if l.strip() and not l.startswith("#") and l.strip() not in ("None", "()")]
    print(f"render {task}:", " ".join(lines))
shutil.rmtree(folder / "_dags_ch05", ignore_errors=True)
