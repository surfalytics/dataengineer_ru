"""Глава 17: две task, два executor. Одна идёт в Celery worker, другая в отдельный pod
со своим image. Нужен values: executor: "CeleryExecutor,KubernetesExecutor"."""
import pendulum
from airflow.sdk import DAG, task
from kubernetes.client import models as k8s

# Свой image только для этой task: pod_override правит pod, который создаст executor
OLD_LIBS = {
    "pod_override": k8s.V1Pod(
        spec=k8s.V1PodSpec(
            containers=[k8s.V1Container(name="base", image="registry:5000/team-a/airflow-libs:1.0")]
        )
    )
}

with DAG(
    dag_id="executors_demo",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    schedule=None,
):

    @task(executor="CeleryExecutor")
    def on_celery():
        print("работаю в общем worker")

    @task(executor="KubernetesExecutor", executor_config=OLD_LIBS)
    def on_k8s():
        print("работаю в своём pod со своим image")

    on_celery() >> on_k8s()
