"""Глава 1: DAG погодного дашборда. Три tasks, расписание раз в день, 2 повтора при сбое."""
from datetime import timedelta

import pendulum
from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG

with DAG(
    dag_id="weather_board",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="@daily",  # расписание: один run на каждый день
    default_args={"retries": 2, "retry_delay": timedelta(minutes=5)},
):
    fetch = BashOperator(task_id="fetch", bash_command="echo fetch forecast")
    clean = BashOperator(task_id="clean", bash_command="echo clean forecast")
    push = BashOperator(task_id="push", bash_command="echo push to dashboard")

    fetch >> clean >> push
