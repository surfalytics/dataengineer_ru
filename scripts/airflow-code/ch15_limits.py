"""Глава 15: как лимиты параллелизма режут число работающих tasks (простая модель, без Airflow).
Лимиты и значения по умолчанию те же, что у Airflow 3."""
PARALLELISM = 32  # все tasks во всей системе
MAX_ACTIVE_TASKS_PER_DAG = 16  # tasks в queued или running на один DAG
DEFAULT_POOL = 128  # слоты default_pool


def running(ready_per_dag):
    """Сколько tasks пойдёт в работу, если у каждого DAG есть столько готовых tasks."""
    total = 0
    for dag, ready in ready_per_dag.items():
        n = min(ready, MAX_ACTIVE_TASKS_PER_DAG)
        total += n
        print(f"{dag}: готово {ready}, лимит DAG даёт {n}")
    n = min(total, PARALLELISM, DEFAULT_POOL)
    print(f"всего в работе: {n} (parallelism {PARALLELISM}, pool {DEFAULT_POOL})")


print("один DAG, 40 готовых tasks")
running({"dag_a": 40})
print("два DAG по 40 готовых tasks")
running({"dag_a": 40, "dag_b": 40})
print("три DAG по 40 готовых tasks")
running({"dag_a": 40, "dag_b": 40, "dag_c": 40})
