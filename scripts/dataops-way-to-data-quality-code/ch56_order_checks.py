"""Проверка заказов. pandas 2.2.3, pandera 0.23.1."""
import pandas as pd
import pandera as pa

schema = pa.DataFrameSchema({
    "order_id": pa.Column(int, unique=True),
    "amount_usd": pa.Column(float, checks=pa.Check.in_range(0.01, 10_000)),
})
orders = pd.DataFrame({"order_id": [101, 101, 102], "amount_usd": [20.0, -2.0, 12.0]})
try:
    schema.validate(orders, lazy=True)
except pa.errors.SchemaErrors as error:
    failed = error.failure_cases.groupby("column").size()
    print(failed.to_string())
