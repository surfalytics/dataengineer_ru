"""DAG загрузки данных в векторную базу: пять DockerOperator с общими параметрами (по главе 14).
Образ и сеть выдуманы. Запуск задач нужен Docker: здесь файл только разбирается DagBag."""
import pendulum
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.sdk import DAG

COLLECTION = "recipes"
DAY_PATH = "s3://data/{{ data_interval_start | ds }}"

docker_kwargs = {
    "image": "vectorflow_cli:latest",
    "environment": {"OPENAI_CONN_TYPE": "openai_api"},
    "docker_url": "tcp://docker-socket-proxy:2375",
    "network_mode": "chapter14_default",
    "auto_remove": "success",
    "tty": True,
}

with DAG(
    dag_id="ch14_ingestion",
    schedule="@daily",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
):
    preprocess = DockerOperator(task_id="preprocess_recipes", command=["preprocess", DAY_PATH], **docker_kwargs)
    create = DockerOperator(
        task_id="create_collection", command=["create", COLLECTION, "text-embedding-3-large"], **docker_kwargs
    )
    compare = DockerOperator(task_id="compare_objects", command=["compare", DAY_PATH, COLLECTION], **docker_kwargs)
    delete = DockerOperator(task_id="delete_outdated_objects", command=["delete", DAY_PATH, COLLECTION], **docker_kwargs)
    save = DockerOperator(task_id="save_recipes_to_weaviate", command=["save", COLLECTION, DAY_PATH], **docker_kwargs)

    preprocess >> create >> compare >> delete >> save
