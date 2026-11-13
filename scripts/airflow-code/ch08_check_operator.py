"""Глава 8: проверка OrdersToS3Operator без PostgreSQL и S3 (hooks заменены mock).
Показывает: str(records) и CSV, что получает S3, и что `replace=True` передан.
Запуск: python3 -I ch08_check_operator.py (нужны apache-airflow 3.4.0 и providers amazon, postgres)."""
import contextlib
import io
import logging
import sys
from pathlib import Path
from unittest import mock

logging.disable(logging.CRITICAL)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch08_orders_to_s3 import OrdersToS3Operator  # noqa: E402

rows = [(1, "Ann", 10.5), (2, "Bob, Jr.", 7.0)]
print("str(records):", str(rows))

op = OrdersToS3Operator(
    task_id="orders_to_s3",
    query="SELECT * FROM orders WHERE order_date = '{{ ds }}'",
    s3_bucket="lake",
    s3_key="orders-{{ ds }}.csv",
)
print("template_fields:", op.template_fields)

with mock.patch("ch08_orders_to_s3.PostgresHook") as pg, mock.patch("ch08_orders_to_s3.S3Hook") as s3:
    pg.return_value.get_records.return_value = rows
    with contextlib.redirect_stdout(io.StringIO()):  # Airflow пишет предупреждение в stdout: прячем его
        op.execute(context={})

kw = s3.return_value.load_file_obj.call_args.kwargs
args = s3.return_value.load_file_obj.call_args.args
print("CSV для S3:", repr(args[0].read().decode()))
print("bucket:", kw["bucket_name"], "| key:", kw["key"], "| replace:", kw["replace"])
print("conn ids:", pg.call_args.kwargs, s3.call_args.kwargs)
