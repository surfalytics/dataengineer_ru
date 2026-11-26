"""Две записи и два чтения таблицы Iceberg с локальным каталогом SQLite."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pyarrow as pa
from pyiceberg.catalog.sql import SqlCatalog
from pyiceberg.schema import Schema
from pyiceberg.types import LongType, NestedField, StringType


def show_history(root: Path) -> None:
    catalog = SqlCatalog(
        "demo",
        uri=f"sqlite:///{root / 'catalog.db'}",
        warehouse=(root / "warehouse").as_uri(),
    )
    catalog.create_namespace("shop")
    table = catalog.create_table(
        "shop.orders",
        schema=Schema(
            NestedField(1, "order_id", LongType(), required=False),
            NestedField(2, "city", StringType(), required=False),
        ),
    )
    table.append(pa.table({"order_id": [1, 2], "city": ["Тула", "Омск"]}))
    first = table.current_snapshot().snapshot_id
    table.append(pa.table({"order_id": [3], "city": ["Тула"]}))

    # Другой читатель загружает таблицу из каталога после второй фиксации.
    reader = catalog.load_table("shop.orders")
    print("Число snapshot:", len(reader.snapshots()))
    for label, snapshot in (("После первой записи", first), ("Сейчас", None)):
        scan = reader.scan(snapshot_id=snapshot, selected_fields=("order_id",))
        ids = sorted(scan.to_arrow().column("order_id").to_pylist())
        print(f"{label}: {ids}")
    print("Файлов данных в текущем snapshot:", len(list(reader.scan().plan_files())))


if __name__ == "__main__":
    with TemporaryDirectory() as directory:
        show_history(Path(directory))
