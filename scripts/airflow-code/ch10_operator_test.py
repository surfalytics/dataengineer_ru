"""Unit-тест оператора с mock. Hook и operator в одном файле, чтобы пример запускался сам."""
from unittest import mock

from airflow.sdk import BaseHook, BaseOperator


class ApiHook(BaseHook):
    def __init__(self, conn_id):
        super().__init__()
        self.conn_id = conn_id

    def fetch(self):
        raise RuntimeError("В тесте сюда ходить нельзя")


class ReportOperator(BaseOperator):
    def __init__(self, conn_id, **kwargs):
        super().__init__(**kwargs)
        self.conn_id = conn_id

    def execute(self, context):
        return len(ApiHook(self.conn_id).fetch())


def test_report_operator_calls_api_once():
    with mock.patch.object(ApiHook, "fetch", return_value=[1, 2, 3]) as fake:
        op = ReportOperator(task_id="report", conn_id="api")
        result = op.execute(context={})

    fake.assert_called_once()
    assert result == 3


if __name__ == "__main__":
    import os
    import sys

    sys.stdout.flush()
    saved = os.dup(1)
    os.dup2(os.open(os.devnull, os.O_WRONLY), 1)  # прячем предупреждения Airflow про вызов вне Task Runner
    try:
        test_report_operator_calls_api_once()
        try:
            ReportOperator(task_id="r2", conn_id="api").execute(context={})
            error = None
        except RuntimeError as e:
            error = e
    finally:
        os.dup2(saved, 1)
    print("test_report_operator_calls_api_once: passed")
    print("без mock оператор упал:", error)
