"""Глава 11: проверка без Docker и Kubernetes.
1. CLI-скрипт запускается через click CliRunner на сгенерированных оценках (seed 11).
2. Файл с DAG разбирается через DagBag. Контейнеры не запускаются.
Запуск: $VENV/bin/python -I ch11_check.py"""
import contextlib
import io
import json
import logging
import random
import sys
import tempfile
from pathlib import Path

logging.disable(logging.CRITICAL)
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from click.testing import CliRunner  # noqa: E402

import ch11_rank_movies as cli  # noqa: E402

rnd = random.Random(11)
ratings = [{"movieId": rnd.choice([10, 20, 30, 40]), "rating": rnd.choice([3.0, 4.0, 4.5, 5.0])} for _ in range(40)]
with tempfile.TemporaryDirectory() as tmp:
    src = Path(tmp) / "ratings" / "2023-01-01.json"
    src.parent.mkdir()
    src.write_text(json.dumps(ratings))
    dst = Path(tmp) / "rankings" / "2023-01-01.csv"  # папки rankings ещё нет
    runner = CliRunner()
    res = runner.invoke(cli.main, ["--input_path", str(src), "--output_path", str(dst), "--top", "3"])
    print("exit code:", res.exit_code)
    print(res.output.strip())
    print(dst.read_text().strip())
    bad = runner.invoke(cli.main, ["--output_path", str(dst)])
    print("без --input_path: exit code", bad.exit_code, "|", bad.output.strip().splitlines()[-1])

from airflow.dag_processing.dagbag import DagBag  # noqa: E402

with contextlib.redirect_stdout(io.StringIO()):
    bag = DagBag(dag_folder=str(HERE / "ch11_docker_dag.py"))
    bag2 = DagBag(dag_folder=str(HERE / "ch11_k8s_dag.py"))
bag.dags.update(bag2.dags)
bag.import_errors.update(bag2.import_errors)
print("DagBag: ошибки импорта:", bag.import_errors or "нет")
for dag_id in sorted(bag.dags):
    d = bag.dags[dag_id]
    ops = {t: type(d.task_dict[t]).__name__ for t in sorted(d.task_dict)}
    print(dag_id, ops, "| rank_movies после", sorted(d.task_dict["rank_movies"].upstream_task_ids))
dk = bag.dags["11_docker_ratings"].task_dict["rank_movies"]
print("docker: image =", dk.image, "| command[0] =", dk.command[0], "| network =", dk.network_mode)
kp = bag.dags["11_kubernetes_ratings"].task_dict["rank_movies"]
print("k8s: image =", kp.image, "| cmds =", kp.cmds, "| on_finish_action =", kp.on_finish_action.value)
