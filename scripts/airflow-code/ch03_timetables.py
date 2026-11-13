"""Глава 3: когда стартует run при trigger и при data interval. Нужен Airflow, сервер не нужен.
Выводит первые три runs для трёх расписаний."""
import contextlib
import io
import logging

import pendulum

logging.disable(logging.CRITICAL)
with contextlib.redirect_stdout(io.StringIO()):
    from airflow.timetables.base import TimeRestriction
    from airflow.timetables.interval import CronDataIntervalTimetable
    from airflow.timetables.trigger import CronTriggerTimetable, DeltaTriggerTimetable

START = pendulum.datetime(2025, 1, 1, tz="UTC")
RESTRICTION = TimeRestriction(earliest=START, latest=pendulum.datetime(2025, 1, 5, tz="UTC"), catchup=True)


def show(title, tt):
    print(title)
    info = tt.next_dagrun_info(last_automated_data_interval=None, restriction=RESTRICTION)
    for _ in range(3):
        di = info.data_interval
        print(f"  run в {info.run_after:%Y-%m-%d %H:%M}; interval [{di.start:%Y-%m-%d %H:%M}, {di.end:%Y-%m-%d %H:%M})")
        info = tt.next_dagrun_info(last_automated_data_interval=di, restriction=RESTRICTION)


show("CronTriggerTimetable:", CronTriggerTimetable("0 0 * * *", timezone="UTC"))
show("CronDataIntervalTimetable:", CronDataIntervalTimetable("0 0 * * *", timezone="UTC"))
show("DeltaTriggerTimetable (раз в 2 дня):", DeltaTriggerTimetable(pendulum.duration(days=2)))
