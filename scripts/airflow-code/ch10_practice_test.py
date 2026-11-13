"""Решения заданий практики главы 10. Запуск: pytest scripts/airflow-code/ch10_practice_test.py"""
import csv
import json
import tempfile
from pathlib import Path
from unittest import mock

from airflow.models import DagBag
from airflow.sdk import BaseHook, BaseOperator


# Задание 1: имя DAG должно начинаться с import или export
def test_dag_name_rule():
    code = (
        "from airflow.sdk import DAG\n"
        "from airflow.providers.standard.operators.empty import EmptyOperator\n"
        "with DAG('report_daily', schedule=None):\n"
        "    EmptyOperator(task_id='a')\n"
    )
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "report.py"
        path.write_text(code)
        bag = DagBag(dag_folder=str(path))
        assert not bag.import_errors
        bad = [d for d in bag.dags if not d.startswith(("import", "export"))]
    assert bad == ["report_daily"]  # правило находит нарушителя


# Задание 2: operator пишет JSON в CSV, тест использует tmp_path
class JsonToCsvOperator(BaseOperator):
    def __init__(self, input_path, output_path, **kwargs):
        super().__init__(**kwargs)
        self.input_path = input_path
        self.output_path = output_path

    def execute(self, context):
        data = json.loads(Path(self.input_path).read_text())
        columns = list(data[0])
        with open(self.output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerows(data)


def test_json_to_csv(tmp_path):
    src, dst = tmp_path / "in.json", tmp_path / "out.csv"
    rows = [{"name": "bob", "age": "41"}, {"name": "alice", "age": "24"}]
    src.write_text(json.dumps(rows))
    JsonToCsvOperator(task_id="t", input_path=src, output_path=dst).execute(context={})
    with open(dst) as f:
        assert list(csv.DictReader(f)) == rows


# Задание 3: патчить надо место вызова, на классе вашего hook
class BaseLike(BaseHook):
    pass


class MyHook(BaseLike):
    def run(self):
        return self.get_connection("x")


def test_patch_on_subclass():
    fake_conn = object()
    with mock.patch.object(MyHook, "get_connection", return_value=fake_conn) as fake:
        assert MyHook().run() is fake_conn
    fake.assert_called_once_with("x")
