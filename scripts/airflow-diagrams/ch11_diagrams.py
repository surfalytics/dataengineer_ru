#!/usr/bin/env python3
"""Глава 11 (Airflow): новая диаграмма. Старые (ch11-container-workflow, ch11-docker-vs-k8s) делает specs/ch11.py.
Usage: python3 scripts/airflow-diagrams/ch11_diagrams.py [name ...]"""
from excb import N, E, Z, T, run_all

D = {}
GRAY = "#495057"

D["ch11-dependencies"] = dict(items=[
    Z("Одно окружение worker: конфликт", 0, 0, 640, 440),
    N("a1", "DAG 1\nнужна библиотека A v1", 40, 70, "p", 260, 90),
    N("a2", "DAG 2\nнужна библиотека A v2", 340, 70, "p", 260, 90),
    N("a3", "В окружении Python\nможет быть одна версия A", 130, 240, "r", 380, 100),
    T("Нужно переписывать DAG или зависимости.", 40, 380, 18, GRAY),
    Z("Контейнеры: свой image у каждой задачи", 760, 0, 640, 440),
    N("b1", "Задача 1\nimage с A v1", 800, 70, "g", 260, 90),
    N("b2", "Задача 2\nimage с A v2", 1100, 70, "g", 260, 90),
    N("b3", "Worker только запускает\nконтейнеры", 890, 240, "y", 380, 100),
    T("Конфликтов нет. На worker ничего ставить не надо.", 800, 380, 18, GRAY),
], edges=[E("a1", "a3"), E("a2", "a3"), E("b1", "b3"), E("b2", "b3")])

if __name__ == "__main__":
    run_all(D)
