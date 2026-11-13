"""Глава 12: Dynamic Task Mapping, pool и явное расписание. Отзывы заменены функцией, сеть не нужна."""
import pendulum
from airflow.sdk import dag, task
from airflow.timetables.trigger import CronTriggerTimetable


@dag(
    dag_id="reviews_mapping",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule=CronTriggerTimetable("0 16 * * *", timezone="UTC"),  # явный timetable, не "@daily"
    catchup=False,
)
def reviews_mapping():
    @task
    def fetch_ratings():
        # число отзывов в день разное: здесь возвращаем три
        return [
            {"movie": "Alpha", "rating": 4.5},
            {"movie": "Beta", "rating": 3.0},
            {"movie": "Gamma", "rating": 5.0},
        ]

    @task(pool="default_pool")  # pool ограничивает число одновременных задач
    def print_rating(rating):
        print(f"MAPPED movie={rating['movie']} rating={rating['rating']}")

    print_rating.expand(rating=fetch_ratings())


reviews_mapping()
