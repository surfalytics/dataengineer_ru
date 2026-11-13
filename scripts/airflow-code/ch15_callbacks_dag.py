"""Глава 15: callback при сбое на уровне DAG и task, общий default_args, свой executor у task."""
import pendulum
from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG


def notify_failure(context):
    # здесь был бы Slack, PagerDuty или email
    ti = context["ti"]
    print(f"ALERT: task {ti.task_id} упала в DAG {ti.dag_id}")


with DAG(
    dag_id="nightly_export",
    schedule="@daily",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    on_failure_callback=notify_failure,  # сработает при падении всего DAG run
    default_args={"on_failure_callback": notify_failure, "retries": 0},  # и для каждой task
) as dag:
    export = BashOperator(
        task_id="export",
        bash_command="exit 1",  # task падает: код возврата не 0
        executor="LocalExecutor",  # executor можно задать для одной task
    )
