"""Глава 3: события пользователей. Data interval по дням, partitions, идемпотентная запись.
API из книги заменён локальной функцией: данные генерируются из даты, сеть не нужна."""
import json
import os
import random
from collections import Counter
from pathlib import Path

import pendulum
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG
from airflow.timetables.interval import CronDataIntervalTimetable

DATA = Path(os.environ.get("EVENTS_DATA", "/tmp/events_demo"))


def _fetch_events(day_start, day_end, output_path):
    """Имитирует /events/range: события только за [day_start, day_end)."""
    rng = random.Random(day_start)  # фиксированный seed от даты
    users = [f"user{rng.randint(1, 3)}" for _ in range(6)]
    events = [{"user": u, "date": day_start} for u in users]
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(events))  # перезаписываем partition: идемпотентно
    print(f"интервал [{day_start}, {day_end}): {len(events)} событий")


def _calculate_stats(input_path, output_path):
    events = json.loads(Path(input_path).read_text())
    stats = Counter((e["date"], e["user"]) for e in events)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{d},{u},{n}" for (d, u), n in sorted(stats.items())]
    Path(output_path).write_text("date,user,events\n" + "\n".join(lines) + "\n")
    print(f"статистика: {len(stats)} строк")


with DAG(
    dag_id="events_daily",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    end_date=pendulum.datetime(2025, 1, 5, tz="UTC"),
    schedule=CronDataIntervalTimetable("0 0 * * *", timezone="UTC"),
    catchup=True,
    max_active_runs=2,
):
    fetch = PythonOperator(
        task_id="fetch_events",
        python_callable=_fetch_events,
        op_kwargs={
            "day_start": "{{ data_interval_start | ds }}",
            "day_end": "{{ data_interval_end | ds }}",
            "output_path": str(DATA) + "/events/{{ data_interval_start | ds }}.json",
        },
    )
    stats = PythonOperator(
        task_id="calculate_stats",
        python_callable=_calculate_stats,
        op_kwargs={
            "input_path": str(DATA) + "/events/{{ data_interval_start | ds }}.json",
            "output_path": str(DATA) + "/stats/{{ data_interval_start | ds }}.csv",
        },
    )
    fetch >> stats
