"""Главa 4: producer и consumer DAG, связанные через asset.
Имена и пути придуманы для примера. Данные не пишем: задача только создаёт событие."""
import pendulum
from airflow.exceptions import AirflowSkipException
from airflow.sdk import DAG, Asset, Metadata, task

START = pendulum.datetime(2025, 1, 1, tz="UTC")

orders = Asset("s3://shop-lake/raw/orders")
payments = Asset("s3://shop-lake/raw/payments")

# Producer: по расписанию, обновляет asset и кладёт дату в extra
with DAG(dag_id="orders_producer", schedule="@daily", start_date=START):

    @task(outlets=[orders])
    def load_orders(logical_date=None):
        yield Metadata(orders, extra={"day": logical_date.strftime("%Y-%m-%d")})

    load_orders()

# Второй producer: пропускает обновление, если данных нет
with DAG(dag_id="payments_producer", schedule="@daily", start_date=START):

    @task(outlets=[payments])
    def load_payments(new_rows=0, logical_date=None):
        if new_rows == 0:
            raise AirflowSkipException("нет новых данных, события не будет")
        yield Metadata(payments, extra={"day": logical_date.strftime("%Y-%m-%d")})

    load_payments()

# Consumer: нет расписания по времени, запуск по событию asset
with DAG(dag_id="orders_report", schedule=[orders], start_date=START):

    @task
    def build_report(triggering_asset_events=None):
        events = triggering_asset_events[orders]
        print("Строим отчёт за", events[0].extra["day"])

    build_report()

# Consumer двух assets: запуск, когда пришли оба события
with DAG(dag_id="revenue_report", schedule=[orders, payments], start_date=START):

    @task
    def join_sources(triggering_asset_events=None):
        days = {a.uri: ev[0].extra["day"] for a, ev in triggering_asset_events.items()}
        print("Даты событий:", days)

    join_sources()
