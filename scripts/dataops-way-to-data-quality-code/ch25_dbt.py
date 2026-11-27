"""Локальная проверка примера главы 25: dbt-core 1.9.8, dbt-duckdb 1.9.2, duckdb 1.3.2."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

import duckdb

PROJECT = Path(__file__).with_name("ch25")


def main():
    with TemporaryDirectory() as directory:
        root = Path(directory)
        project = root / "project"
        shutil.copytree(PROJECT, project)
        database = root / "orders.duckdb"
        env = {
            **os.environ, "BOOK_DBT_DATABASE": str(database),
            "DBT_SEND_ANONYMOUS_USAGE_STATS": "false",
            "DBT_PROFILES_DIR": str(project),
            "DBT_LOG_PATH": str(root / "logs"),
        }

        def run_dbt(*args, expected=0):
            command = [str(Path(sys.executable).with_name("dbt")), *args]
            result = subprocess.run(command, cwd=project, env=env, text=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if result.returncode != expected:
                raise RuntimeError(result.stdout)
            artifact = "sources.json" if args[:2] == ("source", "freshness") else "run_results.json"
            return json.loads((project / "target" / artifact).read_text())["results"]

        build = run_dbt("build")
        tests = [row for row in build if row["unique_id"].startswith("test.")]
        print("Успешных тестов:", sum(row["status"] == "pass" for row in tests))
        fresh = run_dbt("source", "freshness")
        print("Свежесть:", fresh[0]["status"])
        with duckdb.connect(str(database)) as connection:
            connection.execute("delete from line_items where order_id = 2")
        failed = run_dbt("test", "--select", "order_needs_item", expected=1)
        print("Позиций не хватает для заказов:", failed[0]["failures"])


if __name__ == "__main__":
    main()
