"""Пробная миграция Parquet-таблицы Spark в Iceberg без копирования её файлов."""

from pathlib import Path
from tempfile import TemporaryDirectory

from pyspark.sql import SparkSession


def try_snapshot(root: Path) -> None:
    spark = (
        SparkSession.builder.master("local[2]")
        .appName("iceberg-shadow-table")
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
        .config("spark.sql.catalog.lake", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.lake.type", "hadoop")
        .config("spark.sql.catalog.lake.warehouse", (root / "iceberg").as_uri())
        .config("spark.sql.warehouse.dir", (root / "spark").as_uri())
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    try:
        spark.sql("CREATE TABLE default.orders_src (id BIGINT) USING parquet")
        spark.sql("INSERT INTO default.orders_src VALUES (1), (2)")
        spark.sql("CREATE NAMESPACE lake.shop")
        spark.sql("CALL lake.system.snapshot('spark_catalog.default.orders_src', 'lake.shop.orders_test')")
        print("Исходных строк:", spark.table("default.orders_src").count())
        print("Строк в Iceberg:", spark.table("lake.shop.orders_test").count())
        # Сравниваем имена файлов, чтобы не зависеть от формы префикса file:/ или file:///.
        source = {Path(path).name for path in spark.table("default.orders_src").inputFiles()}
        files = spark.sql("SELECT file_path FROM lake.shop.orders_test.files").collect()
        print("Те же файлы:", source == {Path(row.file_path).name for row in files})
    finally:
        spark.stop()


if __name__ == "__main__":
    with TemporaryDirectory() as tmp:
        try_snapshot(Path(tmp))
