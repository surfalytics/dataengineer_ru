"""Глава 7: DAG с PythonSensor. Ждём два условия: файлы данных и маркер _DONE.
Имена выдуманы. Проверка логики: ch07_check_sensor.py (Airflow для неё не нужен)."""
from datetime import timedelta

import pendulum
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.sensors.python import PythonSensor
from airflow.sdk import DAG
from ch07_batch_ready import batch_is_ready


with DAG(
    dag_id="ch07_partner_sensors",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    schedule="0 16 * * *",
    catchup=False,
    max_active_tasks=50,
):
    wait_a = PythonSensor(
        task_id="wait_partner_a",
        python_callable=batch_is_ready,
        op_kwargs={"folder": "/landing/partner_a"},
        poke_interval=300,
        timeout=timedelta(hours=10),  # вместо 7 дней по умолчанию
        mode="reschedule",  # между проверками слот свободен
    )
    process_a = EmptyOperator(task_id="process_partner_a")
    wait_a >> process_a
