"""Глава 8: свой A-to-B operator. Читает заказы из PostgreSQL и кладёт CSV в S3.
Имена выдуманы. Здесь только сам operator, проверка в ch08_check_operator.py."""
import csv
import io

from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.sdk import BaseOperator


class OrdersToS3Operator(BaseOperator):
    template_fields = ("query", "s3_key")

    def __init__(self, query, s3_bucket, s3_key, **kwargs):
        super().__init__(**kwargs)
        self.query = query
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key

    def execute(self, context):
        rows = PostgresHook(postgres_conn_id="shop_db").get_records(self.query)
        text = io.StringIO()
        csv.writer(text, lineterminator="\n").writerows(rows)  # список кортежей -> CSV
        S3Hook(aws_conn_id="lake").load_file_obj(
            io.BytesIO(text.getvalue().encode()),
            bucket_name=self.s3_bucket,
            key=self.s3_key,
            replace=True,  # повторный запуск перезапишет файл, а не упадёт
        )
