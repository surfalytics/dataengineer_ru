"""DAG главы 11 на KubernetesPodOperator. Кластер здесь не запускаем, файл только разбираем (ch11_check.py).
Нужны apache-airflow==3.4.0 и apache-airflow-providers-cncf-kubernetes==11.0.0."""
import os
from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client import models as k8s

USER = os.environ.get("MOVIELENS_USER", "demo")
HOST = os.environ.get("MOVIELENS_HOST", "http://movielens:8081")
PASSWORD = os.environ.get("MOVIELENS_PASSWORD", "demo")

# Те же задачи как pods. Storage берём из PersistentVolumeClaim.
with DAG(
    dag_id="11_kubernetes_ratings",
    start_date=datetime(2023, 1, 1),
    end_date=datetime(2023, 1, 3),
    schedule="@daily",
):
    volume = k8s.V1Volume(
        name="data-volume",
        persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(claim_name="data-volume"),
    )
    volume_mount = k8s.V1VolumeMount(name="data-volume", mount_path="/data", read_only=False)
    k_fetch = KubernetesPodOperator(
        task_id="fetch_ratings",
        name="fetch-ratings",
        namespace="airflow",
        image="manning-airflow/movielens-fetch:1.0",
        cmds=["fetch-ratings"],
        arguments=[
            "--start_date", "{{ data_interval_start | ds }}",
            "--end_date", "{{ data_interval_end | ds }}",
            "--output_path", "/data/ratings/{{ data_interval_start | ds }}.json",
            "--user", USER, "--password", PASSWORD, "--host", HOST,
        ],
        in_cluster=False,
        volumes=[volume],
        volume_mounts=[volume_mount],
        image_pull_policy="IfNotPresent",
        on_finish_action="delete_pod",
    )
    k_rank = KubernetesPodOperator(
        task_id="rank_movies",
        name="rank-movies",
        namespace="airflow",
        image="manning-airflow/movielens-rank:1.0",
        cmds=["rank-movies"],
        arguments=[
            "--input_path", "/data/ratings/{{ data_interval_start | ds }}.json",
            "--output_path", "/data/rankings/{{ data_interval_start | ds }}.csv",
        ],
        in_cluster=False,
        volumes=[volume],
        volume_mounts=[volume_mount],
        image_pull_policy="IfNotPresent",
        on_finish_action="delete_pod",
    )
    k_fetch >> k_rank
