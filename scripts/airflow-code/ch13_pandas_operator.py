"""Глава 13: PandasOperator из книги (read -> transform -> write вокруг DataFrame).
MinIO заменён строкой и буфером в памяти, чтобы пример шёл без Docker.
Запуск: $VENV/bin/python -I ch13_pandas_operator.py  (apache-airflow==3.4.0, pandas==2.3.3)"""
import io
import pandas as pd
from airflow.sdk import BaseOperator

CSV = """pickup_datetime,dropoff_datetime,pickup_locationid,dropoff_locationid,trip_distance
2024-09-19 18:55:06,2024-09-19 19:05:38,230,68,1.00
2024-09-19 18:50:29,2024-09-19 19:02:07,48,239,1.86
"""


class PandasOperator(BaseOperator):
    template_fields = ("_input_callable_kwargs", "_transform_callable_kwargs", "_output_callable_kwargs")

    def __init__(self, input_callable, output_callable, transform_callable=None,
                 input_callable_kwargs=None, transform_callable_kwargs=None,
                 output_callable_kwargs=None, **kwargs):
        super().__init__(**kwargs)
        self._input_callable = input_callable
        self._input_callable_kwargs = input_callable_kwargs or {}
        self._transform_callable = transform_callable
        self._transform_callable_kwargs = transform_callable_kwargs or {}
        self._output_callable = output_callable
        self._output_callable_kwargs = output_callable_kwargs or {}

    def execute(self, context):
        df = self._input_callable(**self._input_callable_kwargs)
        print("Read DataFrame with shape:", df.shape)
        if self._transform_callable:
            df = self._transform_callable(df, **self._transform_callable_kwargs)
            print("DataFrame shape after transform:", df.shape)
        self._output_callable(df, **self._output_callable_kwargs)


def read_text(pandas_read_callable, text):
    return pandas_read_callable(io.StringIO(text))


def transform_taxi_data(df):
    return (
        df.assign(
            starttime=lambda d: pd.to_datetime(d.pickup_datetime),
            stoptime=lambda d: pd.to_datetime(d.dropoff_datetime),
            tripduration=lambda d: (d.stoptime - d.starttime).dt.total_seconds().astype(int),
        )
        .rename(columns={"pickup_locationid": "start_location_id", "dropoff_locationid": "end_location_id"})
        .drop(columns=["trip_distance", "pickup_datetime", "dropoff_datetime"])
    )


def write_text(df, sink):
    sink.append(df.to_csv(index=False))


sink = []
op = PandasOperator(
    task_id="process_taxi_data",
    input_callable=read_text,
    input_callable_kwargs={"pandas_read_callable": pd.read_csv, "text": CSV},
    transform_callable=transform_taxi_data,
    output_callable=write_text,
    output_callable_kwargs={"sink": sink},
)
print("template_fields:", op.template_fields)
# execute() вызывают task runner; здесь берём исходную функцию без обёртки
type(op).execute.__wrapped__(op, {})
print(sink[0], end="")
