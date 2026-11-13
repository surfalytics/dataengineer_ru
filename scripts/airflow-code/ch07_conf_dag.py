"""Глава 7: один DAG обслуживает всех через dag_run.conf. Запуск только вручную или через API."""
import pendulum
from airflow.sdk import DAG, task


with DAG(
    dag_id="ch07_conf_demo",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    schedule=None,  # DAG зависит от conf, поэтому расписания нет
):

    @task
    def process(**context):
        conf = context["dag_run"].conf
        print("обрабатываем супермаркет:", conf["supermarket_id"])

    process()
