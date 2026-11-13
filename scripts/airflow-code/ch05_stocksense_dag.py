"""Глава 5: templating в BashOperator и PythonOperator (без сети: URL только печатается)."""
import pendulum
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG
from airflow.timetables.interval import CronDataIntervalTimetable

URL = (
    "https://dumps.wikimedia.org/other/pageviews/"
    "{year}/{year}-{month:0>2}/pageviews-{year}{month:0>2}{day:0>2}-{hour:0>2}0000.gz"
)


def _get_data(year, month, day, hour, output_path, data_interval_start, **context):
    # year..hour пришли из op_kwargs уже отрисованными; data_interval_start берётся из context
    url = URL.format(year=year, month=month, day=day, hour=hour)
    print(f"url: {url}")
    print(f"output_path: {output_path}")
    print(f"interval: {data_interval_start} -> {context['data_interval_end']}")


with DAG(
    dag_id="stocksense_templating",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule=CronDataIntervalTimetable("@hourly", timezone="UTC"),
    catchup=False,
):
    # BashOperator: bash_command входит в template_fields, Jinja подставляет {{ ... }}
    show_name = BashOperator(
        task_id="show_name",
        bash_command=(
            "echo pageviews-{{ logical_date.format('YYYYMMDD') }}-"
            "{{ '{:02}'.format(logical_date.hour) }}0000.gz"
        ),
    )
    # PythonOperator: строки в op_kwargs шаблонизируются, функция получает уже готовые значения
    get_data = PythonOperator(
        task_id="get_data",
        python_callable=_get_data,
        op_kwargs={
            "year": "{{ logical_date.year }}",
            "month": "{{ logical_date.month }}",
            "day": "{{ logical_date.day }}",
            "hour": "{{ logical_date.hour }}",
            "output_path": "/tmp/wikipageviews-{{ logical_date.format('YYYYMMDDHH') }}.gz",
        },
    )
    show_name >> get_data
