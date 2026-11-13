#!/usr/bin/env python3
"""Глава 10 (Airflow): новые диаграммы. Старые (ch10-ci-pipeline, ch10-mock-or-docker) делает specs/ch10.py.
Usage: python3 scripts/airflow-diagrams/ch10_diagrams.py [name ...]"""
from excb import N, E, Z, T, run_all

D = {}
GRAY = "#495057"

# ---------- Fig 10.6, листинг 10.18: где патчить ----------
D["ch10-where-to-patch"] = dict(items=[
    T("Mock ставят там, где метод вызывают, а не там, где он объявлен", 0, -50, 22, "#1971c2"),
    N("op", "MovielensPopularityOperator\nexecute() вызывает hook", 0, 0, "p", 330, 100),
    N("hook", "MovielensHook\nget_connection() вызывают здесь", 450, 0, "g", 330, 100),
    N("base", "BaseHook\nget_connection() объявлен здесь", 900, 0, "r", 330, 100),
    N("ok", "mocker.patch.object(\nMovielensHook, \"get_connection\")\nправильно", 450, 220, "g", 330, 110),
    N("bad", "mocker.patch.object(\nBaseHook, \"get_connection\")\nчастая ошибка", 900, 220, "r", 330, 110),
    T("Hook наследует метод от BaseHook, но оператор обращается к классу своего hook.", 0, 380, 20, GRAY),
], edges=[E("op", "hook", "вызывает"), E("hook", "base", "наследует", dashed=True),
          E("hook", "ok"), E("base", "bad")])

# ---------- 10.4: три способа проверить весь DAG ----------
D["ch10-whole-dag"] = dict(items=[
    T("Как проверить, что все task в DAG работают вместе", 0, -50, 22, "#1971c2"),
    N("dagtest", "dag.test()\nзапуск DAG из кода или pytest", 0, 0, "g", 330, 100),
    N("whirl", "Whirl\nкопия production в Docker Compose", 450, 0, "pu", 330, 100),
    N("dtap", "DTAP\nотдельные окружения и ветки Git", 900, 0, "y", 330, 100),
    N("d1", "Быстро, всё в одном процессе.\nВнешние системы: mock или контейнер", 0, 160, "n", 330, 100),
    N("w1", "Много сервисов как контейнеры.\nНе всё есть образом (например GCS)", 450, 160, "n", 330, 100),
    N("t1", "Тяжело вести.\nМалые команды берут два окружения", 900, 160, "n", 330, 100),
    T("Чем реальнее окружение, тем дороже его вести.", 0, 310, 20, GRAY),
], edges=[E("dagtest", "d1", head=False, dashed=True), E("whirl", "w1", head=False, dashed=True),
          E("dtap", "t1", head=False, dashed=True)])

if __name__ == "__main__":
    run_all(D)
