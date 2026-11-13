"""Глава 2: DAG про запуски ракет, версия без сети.
Те же три tasks, что в книге: download_launches >> get_pictures >> notify.
Вместо Launch Library API берём маленький JSON, который пишет первая task."""
import json
import os
import pathlib

import pendulum
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG

WORK = pathlib.Path(os.environ.get("ROCKET_DIR", "/tmp/rockets"))  # рабочая папка


def _get_pictures():
    """Читает JSON и 'скачивает' картинки: пишет по файлу на каждый url."""
    (WORK / "images").mkdir(parents=True, exist_ok=True)
    launches = json.loads((WORK / "launches.json").read_text())
    for launch in launches["results"]:
        name = launch["image"].split("/")[-1]
        (WORK / "images" / name).write_text("fake image")
        print(f"Saved {launch['image']} as {name}")  # print попадёт в логи task


with DAG(
    dag_id="rocket_launches",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule=None,  # запуск только вручную
):
    download_launches = BashOperator(
        task_id="download_launches",
        bash_command=(
            f"mkdir -p {WORK} && echo "
            "'{\"results\": [{\"image\": \"https://x.org/falcon9.jpg\"},"
            " {\"image\": \"https://x.org/electron.jpg\"}]}' "
            f"> {WORK}/launches.json"
        ),
    )
    get_pictures = PythonOperator(task_id="get_pictures", python_callable=_get_pictures)
    notify = BashOperator(
        task_id="notify",
        bash_command=f'echo "There are $(ls {WORK}/images | wc -l) images."',
    )

    download_launches >> get_pictures >> notify
