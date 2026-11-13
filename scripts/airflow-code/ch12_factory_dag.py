"""Глава 12: фабрика задач, фабрика DAG и TaskGroup."""
import pendulum
from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG, TaskGroup
from airflow.timetables.trigger import CronTriggerTimetable

START = pendulum.datetime(2025, 1, 1, tz="UTC")


def generate_tasks(dataset_name, dag):
    """Фабрика задач: цепочка fetch >> preprocess. Возвращает первую и последнюю задачу."""
    fetch = BashOperator(task_id=f"fetch_{dataset_name}", bash_command=f"echo fetch {dataset_name}", dag=dag)
    prep = BashOperator(task_id=f"preprocess_{dataset_name}", bash_command=f"echo preprocess {dataset_name}", dag=dag)
    fetch >> prep
    return fetch, prep


def generate_dag(dataset_name):
    """Фабрика DAG: возвращает готовый DAG."""
    with DAG(
        dag_id=f"factory_{dataset_name}",
        start_date=START,
        schedule=CronTriggerTimetable("0 16 * * *", timezone="UTC"),
    ) as dag:
        generate_tasks(dataset_name, dag)
    return dag


# несколько DAG из одного файла: у каждого своё имя в globals(), иначе виден только последний
for name in ["sales", "customers"]:
    globals()[f"factory_{name}"] = generate_dag(name)

# один DAG, в нём TaskGroup на каждый набор данных
with DAG(
    dag_id="grouped",
    start_date=START,
    schedule=CronTriggerTimetable("0 16 * * *", timezone="UTC"),
) as grouped:
    for name in ["sales", "customers"]:
        with TaskGroup(name, tooltip=f"Задачи набора {name}"):
            generate_tasks(name, grouped)
