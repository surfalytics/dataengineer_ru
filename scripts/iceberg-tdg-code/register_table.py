"""Перенос регистрации локальной Iceberg-таблицы в пустой JDBC-каталог."""

from pathlib import Path
from tempfile import TemporaryDirectory

from pyspark.sql import SparkSession


def run(root: Path) -> None:
    spark = (
        SparkSession.builder.master("local[2]")
        .appName("iceberg-register-table")
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
        .config("spark.sql.catalog.demo", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.demo.type", "hadoop")
        .config("spark.sql.catalog.demo.warehouse", (root / "source").as_uri())
        .config("spark.sql.catalog.target", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.target.type", "jdbc")
        .config("spark.sql.catalog.target.uri", f"jdbc:sqlite:{root / 'catalog.db'}")
        .config("spark.sql.catalog.target.warehouse", (root / "target").as_uri())
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    try:
        spark.sql("CREATE NAMESPACE demo.shop")
        spark.sql("""
            CREATE TABLE demo.shop.orders (
              id BIGINT, ordered_at TIMESTAMP, amount DECIMAL(10, 2)
            ) USING iceberg PARTITIONED BY (days(ordered_at))
        """)
        spark.sql("INSERT INTO demo.shop.orders VALUES (1, TIMESTAMP '2024-05-01 10:00:00', 15.00)")
        # С этого места запись в исходный каталог остановлена.
        loc = spark.sql("""
            SELECT file FROM demo.shop.orders.metadata_log_entries
            ORDER BY timestamp DESC LIMIT 1
        """).first().file
        spark.sql("CREATE NAMESPACE target.db")
        spark.sql(f"CALL target.system.register_table(table => 'db.orders', metadata_file => '{loc}')")
        print("Новый каталог:", spark.sql("SELECT COUNT(*) FROM target.db.orders").first()[0])
        print("Сумма:", spark.sql("SELECT SUM(amount) FROM target.db.orders").first()[0])
    finally:
        spark.stop()


if __name__ == "__main__":
    with TemporaryDirectory() as tmp:
        run(Path(tmp))
