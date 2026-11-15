"""Глава 1: простой DAG Airflow из двух задач (аналог Example 1-2, API Airflow 3)."""
from datetime import datetime, timedelta

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG

default_args = {
    "owner": "analytics",
    "depends_on_past": False,          # запуск не ждёт успеха прошлого запуска
    "retries": 1,                      # одна повторная попытка при сбое
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="hourly_demo",
    start_date=datetime(2026, 1, 1),
    schedule=timedelta(hours=1),       # раз в час
    catchup=False,
    default_args=default_args,
) as dag:
    print_date = BashOperator(task_id="print_date", bash_command="date")
    pause = BashOperator(task_id="pause", bash_command="sleep 5", retries=3)

    print_date >> pause                # pause стартует только после успеха print_date
