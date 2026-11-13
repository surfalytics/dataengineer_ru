"""Глава 9: DAG с sensor, deferrable sensor и своим operator. Нужен ch09_components.py рядом."""
import pendulum
from airflow.sdk import DAG
from ch09_components import OrdersFetchOperator, OrdersSensor, OrdersSensorAsync

with DAG(
    dag_id="orders_custom",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    schedule="@daily",
):
    wait = OrdersSensor(task_id="wait_for_orders", conn_id="shop_api", mode="reschedule")
    wait_async = OrdersSensorAsync(task_id="wait_for_orders_async", conn_id="shop_api")
    fetch = OrdersFetchOperator(
        task_id="fetch_orders",
        conn_id="shop_api",
        output_path="/tmp/orders/{{ ds }}.json",
    )
    wait >> fetch
    wait_async >> fetch
