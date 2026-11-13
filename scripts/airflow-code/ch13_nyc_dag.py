"""Глава 13: каркас DAG проекта. Скачивание идёт в MinIO через S3Hook (нужны Docker Compose книги).
Здесь проверяется только разбор DAG. Импорты провайдеров лежат внутри функций."""
import pendulum
from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator


def _download_citi_bike_data(data_interval_start, **_):
    import json

    import requests
    from airflow.hooks.base import BaseHook
    from airflow.providers.amazon.aws.hooks.s3 import S3Hook
    from requests.auth import HTTPBasicAuth

    conn = BaseHook.get_connection("citibike")
    url = f"http://{conn.host}:{conn.port}/recent/minute/15"
    data = requests.get(url, auth=HTTPBasicAuth(conn.login, conn.password)).json()
    S3Hook(aws_conn_id="s3").load_string(
        string_data=json.dumps(data),
        key=f"raw/citibike/{data_interval_start.strftime('%Y%m%dT%H%M%S')}.json",
        bucket_name="datalake",
        replace=True,  # повтор не падает
    )


def _download_taxi_data():
    import requests
    from airflow.hooks.base import BaseHook
    from airflow.providers.amazon.aws.hooks.s3 import S3Hook

    url = f"http://{BaseHook.get_connection('taxi').host}"
    s3_hook = S3Hook(aws_conn_id="s3")
    for name in [f["name"] for f in requests.get(url).json()]:
        text = requests.get(f"{url}/{name}").text
        s3_hook.load_string(string_data=text, key=f"raw/taxi/{name}", bucket_name="datalake", replace=True)


with DAG(
    dag_id="nyc_dag",
    schedule="*/15 * * * *",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
):
    PythonOperator(task_id="download_citi_bike_data", python_callable=_download_citi_bike_data)
    PythonOperator(task_id="download_taxi_data", python_callable=_download_taxi_data)
