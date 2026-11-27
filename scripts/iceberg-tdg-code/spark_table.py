"""Создать локальную таблицу Iceberg, выполнить MERGE и прочитать старый snapshot."""

from pathlib import Path
from tempfile import TemporaryDirectory

from pyspark.sql import SparkSession


def run(warehouse: Path) -> None:
    spark = (
        SparkSession.builder.master("local[2]")
        .appName("iceberg-book-example")
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
        .config("spark.sql.catalog.catalog", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.catalog.type", "hadoop")
        .config("spark.sql.catalog.catalog.warehouse", warehouse.as_uri())
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    try:
        spark.sql("CREATE NAMESPACE catalog.db")
        spark.sql("USE catalog.db")
        spark.sql("""
            CREATE TABLE orders (
                order_id BIGINT, customer_id BIGINT,
                order_amount DECIMAL(10, 2), order_ts TIMESTAMP
            ) USING iceberg PARTITIONED BY (hours(order_ts))
        """)
        spark.sql("INSERT INTO orders VALUES (1, 7, 19.00, TIMESTAMP '2024-05-01 10:15:00')")
        first = spark.sql("SELECT snapshot_id FROM catalog.db.orders.snapshots").first().snapshot_id
        spark.sql("""
            CREATE TEMP VIEW orders_staging AS SELECT * FROM VALUES
                (1L, 7L, 22.00, TIMESTAMP '2024-05-01 10:15:00'),
                (2L, 8L, 15.00, TIMESTAMP '2024-05-01 10:25:00')
            AS t(order_id, customer_id, order_amount, order_ts)
        """)
        spark.sql("""
            MERGE INTO orders AS target USING orders_staging AS source
            ON target.order_id = source.order_id
            WHEN MATCHED THEN UPDATE SET target.order_amount = source.order_amount
            WHEN NOT MATCHED THEN INSERT *
        """)
        for label, table in (("До MERGE", f"orders VERSION AS OF {first}"), ("После MERGE", "orders")):
            rows = spark.sql(f"SELECT order_id, order_amount FROM {table} ORDER BY order_id").collect()
            print(label, [(r.order_id, str(r.order_amount)) for r in rows])
        stats = spark.sql("""
            CALL catalog.system.rewrite_data_files(table => 'db.orders', strategy => 'binpack')
        """).first()
        print("Файлов переписано:", stats.rewritten_data_files_count)
    finally:
        spark.stop()


if __name__ == "__main__":
    with TemporaryDirectory() as tmp:
        run(Path(tmp) / "warehouse")
