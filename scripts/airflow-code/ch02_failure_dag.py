"""Глава 2: DAG, в котором get_pictures всегда падает (как при обрыве сети)."""
import pendulum
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG


def _get_pictures():
    raise ConnectionError("Could not connect to https://x.org/falcon9.jpg")


with DAG(dag_id="rocket_failure", start_date=pendulum.datetime(2025, 1, 1, tz="UTC"), schedule=None):
    download = BashOperator(task_id="download_launches", bash_command="echo ok")
    pictures = PythonOperator(task_id="get_pictures", python_callable=_get_pictures)
    notify = BashOperator(task_id="notify", bash_command="echo done")
    download >> pictures >> notify
