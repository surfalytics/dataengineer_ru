#!/usr/bin/env python3
"""Глава 8 (Airflow): новые диаграммы. Старые (ch08-ml-pipeline, ch08-a-to-b) делает specs/ch08.py.
Usage: python3 scripts/airflow-diagrams/ch08_diagrams.py [name ...]"""
from excb import N, E, Z, T, run_all

D = {}
GRAY = "#495057"

# ---------- Fig 8.8: wait_for_completion ----------
D["ch08-wait-completion"] = dict(items=[
    Z("wait_for_completion=False: fire and forget", 0, 0, 1060, 210),
    N("a1", "task запускает\ntraining job", 40, 70, "p", 240, 90),
    N("a2", "task сразу\nsuccess", 400, 70, "g", 240, 90),
    N("a3", "job в AWS\nможет упасть", 760, 70, "r", 240, 90),
    Z("wait_for_completion=True: опрос каждые check_interval секунд", 0, 280, 1060, 210),
    N("b1", "task запускает\ntraining job", 40, 350, "p", 240, 90),
    N("b2", "опрос AWS:\njob ещё идёт?", 400, 350, "y", 240, 90),
    N("b3", "success или failed\nпо итогу job", 760, 350, "g", 240, 90),
    T("Downstream tasks стартуют только после настоящего конца job.", 0, 520, 20, GRAY),
], edges=[E("a1", "a2"), E("a2", "a3", "не знаем", dashed=True),
          E("b1", "b2"), E("b2", "b3", "конец job")])

# ---------- Orchestration и execution ----------
D["ch08-orchestration-execution"] = dict(items=[
    Z("Airflow: orchestration", 0, 0, 380, 330),
    N("af", "worker запускает job\nи ждёт результат", 40, 90, "p", 300, 100),
    T("Работы с данными не делает", 40, 230, 18, GRAY),
    Z("Другая система: execution", 560, 0, 760, 330),
    N("sp", "Spark\n(spark-submit, SSH, Livy)", 600, 60, "g", 330, 90),
    N("dk", "контейнер\n(DockerOperator)", 600, 200, "g", 330, 90),
    N("st", "S3 / warehouse\nданные", 1000, 130, "db", 270, 100),
    T("Тяжёлая работа не занимает ресурсы машины Airflow. Контейнер удаляют после запуска.", 0, 370, 20, GRAY),
], edges=[E("af", "sp", "запуск"), E("af", "dk", "запуск"), E("sp", "st"), E("dk", "st")])

if __name__ == "__main__":
    run_all(D)
