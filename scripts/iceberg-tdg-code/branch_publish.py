"""Проверить запись в ветку и публикацию прошедших проверку данных."""

from pathlib import Path
from tempfile import TemporaryDirectory

from pyspark.sql import SparkSession


def run(root: Path) -> None:
    spark = (
        SparkSession.builder.master("local[2]").appName("iceberg-branch-publish")
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
        .config("spark.sql.catalog.lake", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.lake.type", "hadoop")
        .config("spark.sql.catalog.lake.warehouse", root.as_uri())
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    try:
        spark.sql("CREATE NAMESPACE lake.shop")
        spark.sql("CREATE TABLE lake.shop.orders (id BIGINT, amount INT) USING iceberg")
        spark.sql("INSERT INTO lake.shop.orders VALUES (1, 10)")
        spark.sql("ALTER TABLE lake.shop.orders CREATE BRANCH audit")
        spark.sql("INSERT INTO lake.shop.orders.branch_audit VALUES (2, 25)")
        draft = spark.table("lake.shop.orders.branch_audit")
        print("Строк до публикации:", spark.table("lake.shop.orders").count())
        print("Строк в ветке:", draft.count())
        if draft.filter("amount IS NULL OR amount < 0").count():
            raise ValueError("Проверка суммы заказа не пройдена")
        spark.sql("CALL lake.system.fast_forward('shop.orders', 'main', 'audit')")
        print("Строк после публикации:", spark.table("lake.shop.orders").count())
    finally:
        spark.stop()


if __name__ == "__main__":
    with TemporaryDirectory() as tmp:
        run(Path(tmp))
