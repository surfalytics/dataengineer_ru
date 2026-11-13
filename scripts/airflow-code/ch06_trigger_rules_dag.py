"""Глава 6: как trigger rules реагируют на upstream-задачи со статусами success, failed, skipped."""
import pendulum
from airflow.exceptions import AirflowSkipException
from airflow.sdk import DAG, task

with DAG(dag_id="trigger_rules_demo", schedule=None, start_date=pendulum.datetime(2025, 1, 1, tz="UTC")):

    @task
    def up_ok():
        return "ok"

    @task
    def up_skip():
        raise AirflowSkipException("пропускаем")

    @task
    def up_fail():
        raise RuntimeError("сбой")

    def downstream(name, rule):
        @task(task_id=name, trigger_rule=rule)
        def step():
            return name

        return step()

    ok, skip, fail = up_ok(), up_skip(), up_fail()
    # случай A: один upstream успешен, другой пропущен
    [ok, skip] >> downstream("a_all_success", "all_success")
    [ok, skip] >> downstream("a_none_failed", "none_failed")
    # случай B: один upstream успешен, другой упал
    for rule in ("all_success", "none_failed", "all_done", "one_failed"):
        [ok, fail] >> downstream(f"b_{rule}", rule)
