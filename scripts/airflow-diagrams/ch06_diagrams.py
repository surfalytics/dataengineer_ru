#!/usr/bin/env python3
"""Глава 6 (Airflow): новые диаграммы. Старые (ch06-branching, ch06-trigger-rules) делает specs/ch06.py.
Usage: python3 scripts/airflow-diagrams/ch06_diagrams.py [name ...]"""
from excb import N, E, Z, T, run_all

D = {}
GRAY = "#495057"

# ---------- Fig 6.2-6.4: fan-out, fan-in и порядок выполнения ----------
D["ch06-fanout-fanin"] = dict(items=[
    T("Umbrella DAG: fan-out после start, fan-in в join_datasets", 0, -50, 22, "#1971c2"),
    N("start", "1. start", 0, 120, "n", 200, 80),
    N("fw", "2a. fetch_weather", 330, 20, "p", 260, 80),
    N("cw", "3a. clean_weather", 680, 20, "p", 260, 80),
    N("fs", "2b. fetch_sales", 330, 230, "p", 260, 80),
    N("cs", "3b. clean_sales", 680, 230, "p", 260, 80),
    N("join", "4. join_datasets", 1030, 120, "g", 260, 80),
    N("train", "5. train_model", 1380, 120, "y", 240, 80),
    N("dep", "6. deploy_model", 1710, 120, "y", 240, 80),
    T("Fan-out: start запускает две ветки параллельно.", 0, 380, 20, GRAY),
    T("Fan-in: join_datasets ждёт обе ветки. Номер 3b может начаться раньше 2a.", 0, 415, 20, GRAY),
], edges=[E("start", "fw"), E("start", "fs"), E("fw", "cw"), E("fs", "cs"),
          E("cw", "join"), E("cs", "join"), E("join", "train"), E("train", "dep")])

# ---------- Fig 6.16-6.19: XCom и Taskflow ----------
D["ch06-xcom-taskflow"] = dict(items=[
    T("Как train_model передаёт model_id в deploy_model", 0, -50, 22, "#1971c2"),
    Z("Обычный API: xcom_push и xcom_pull", -20, 0, 900, 260),
    N("t1", "train_model\nxcom_push(key, value)", 20, 70, "p", 260, 90),
    N("x1", "XCom в metastore\nkey=model_id", 340, 70, "n", 240, 90),
    N("d1", "deploy_model\nxcom_pull(task_ids, key)", 620, 70, "p", 260, 90),
    T("Ключ записан в двух местах. Связи нет в графе.", 330, 200, 18, "#e03131"),
    Z("Taskflow API: return и аргумент", -20, 330, 900, 260),
    N("t2", "@task train_model\nreturn model_id", 20, 400, "g", 260, 90),
    N("x2", "XCom\nAirflow ведёт сам", 340, 400, "n", 240, 90),
    N("d2", "@task deploy_model\n(model_id)", 620, 400, "g", 260, 90),
    T("Связь строится из вызова deploy_model(train_model()).", 330, 530, 18, "#2f9e44"),
], edges=[E("t1", "x1"), E("x1", "d1"), E("t2", "x2"), E("x2", "d2")])

if __name__ == "__main__":
    run_all(D)
