"""Глава 6: umbrella DAG с fan-out, веткой по ERP, join, LatestOnly и Taskflow XCom."""
import pendulum
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.latest_only import LatestOnlyOperator
from airflow.sdk import dag, task

ERP_CHANGE_DATE = pendulum.datetime(2025, 6, 1, tz="UTC")


@dag(dag_id="umbrella_branch", schedule="@daily", start_date=pendulum.datetime(2025, 1, 1, tz="UTC"))
def umbrella_branch():
    start = EmptyOperator(task_id="start")

    @task
    def fetch_weather():
        return "weather.csv"

    @task.branch
    def pick_erp_system(data_interval_start=None):
        # возвращаем task_id ветки, которая должна выполниться
        if data_interval_start < ERP_CHANGE_DATE:
            return "fetch_sales_old"
        return "fetch_sales_new"

    @task
    def fetch_sales_old():
        return "sales_old.csv"

    @task
    def fetch_sales_new():
        return "sales_new.csv"

    # один join после ветки: правило none_failed ставим только на нём
    join_erp_branch = EmptyOperator(task_id="join_erp_branch", trigger_rule="none_failed")
    join_datasets = EmptyOperator(task_id="join_datasets")

    @task
    def train_model(ds=None):
        return f"model-{ds}"  # return кладёт значение в XCom

    @task
    def deploy_model(model_id: str):
        print("deploy", model_id)  # model_id пришёл из XCom

    pick = pick_erp_system()
    old, new = fetch_sales_old(), fetch_sales_new()
    model_id = train_model()
    latest_only = LatestOnlyOperator(task_id="latest_only")

    weather = fetch_weather()
    start >> [weather, pick]  # fan-out
    pick >> [old, new] >> join_erp_branch
    [weather, join_erp_branch] >> join_datasets  # fan-in
    join_datasets >> model_id >> latest_only >> deploy_model(model_id)


umbrella_branch()
