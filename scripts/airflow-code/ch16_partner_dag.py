import pendulum
from airflow.providers.http.operators.http import HttpOperator
from airflow.sdk import DAG

with DAG(
    dag_id="call_partner_api",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    schedule=None,
):
    ping = HttpOperator(
        task_id="ping",
        http_conn_id="partner_api",  # секрет лежит в backend
        method="GET",
        endpoint="health",
    )
