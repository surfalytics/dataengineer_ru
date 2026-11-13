"""Глава 12: connection читаем внутри task, а не в теле файла DAG."""
from airflow.sdk import BaseHook, task


@task
def call_api():
    conn = BaseHook.get_connection("my_api")  # БД читаем при запуске task, а не при парсинге
    return conn.host
