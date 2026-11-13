"""DAG главы 11 на DockerOperator. Docker здесь не запускаем, файл только разбираем (ch11_check.py).
Нужны apache-airflow==3.4.0 и apache-airflow-providers-docker==4.6.1."""
import os
from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

USER = os.environ.get("MOVIELENS_USER", "demo")
HOST = os.environ.get("MOVIELENS_HOST", "http://movielens:8081")
PASSWORD = os.environ.get("MOVIELENS_PASSWORD", "demo")

# Данные между задачами идут через общий volume.
with DAG(
    dag_id="11_docker_ratings",
    start_date=datetime(2023, 1, 1),
    end_date=datetime(2023, 1, 3),
    schedule="@daily",
):
    fetch_ratings = DockerOperator(
        task_id="fetch_ratings",
        image="manning-airflow/movielens-fetch:1.0",
        command=[
            "fetch-ratings",
            "--start_date", "{{ data_interval_start | ds }}",
            "--end_date", "{{ data_interval_end | ds }}",
            "--output_path", "/data/ratings/{{ logical_date | ds }}.json",
            "--user", USER, "--password", PASSWORD, "--host", HOST,
        ],
        mounts=[Mount(source="docker_airflow-data-volume", target="/data", type="volume")],
        network_mode="docker_default",
    )
    rank_movies = DockerOperator(
        task_id="rank_movies",
        image="manning-airflow/movielens-rank:1.0",
        command=[
            "rank-movies",
            "--input_path", "/data/ratings/{{ data_interval_start | ds }}.json",
            "--output_path", "/data/rankings/{{ data_interval_start | ds }}.csv",
        ],
        mounts=[Mount(source="docker_airflow-data-volume", target="/data", type="volume")],
        network_mode="docker_default",
    )
    fetch_ratings >> rank_movies
