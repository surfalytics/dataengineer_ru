"""Глава 12: pandas UDF с type hints, Iterator, mapInPandas, applyInPandas."""
import os, sys
from typing import Iterator
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import pandas_udf

os.environ["PYSPARK_PYTHON"] = sys.executable
spark = (SparkSession.builder.master("local[2]").appName("ch12-pandas")
         .config("spark.ui.enabled", "false").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")


@pandas_udf("long")
def plus_one(v: pd.Series) -> pd.Series:
    return v + 1


df = spark.range(3)
df.withColumn("plus_one", plus_one("id")).orderBy("id").show()


@pandas_udf("long")
def plus_one_iter(batches: Iterator[pd.Series]) -> Iterator[pd.Series]:
    offset = 1  # здесь в реальной задаче загружают модель: один раз на процесс
    for s in batches:
        yield s + offset


df.withColumn("plus_one", plus_one_iter("id")).orderBy("id").show()


def keep_one(batches: Iterator[pd.DataFrame]) -> Iterator[pd.DataFrame]:
    for pdf in batches:
        yield pdf[pdf.id == 1]


df.mapInPandas(keep_one, schema=df.schema).show()

df1 = spark.createDataFrame(
    [(1201, 1, 1.0), (1201, 2, 2.0), (1202, 1, 3.0), (1202, 2, 4.0)], ("time", "id", "v1"))
df2 = spark.createDataFrame([(1201, 1, "x"), (1201, 2, "y")], ("time", "id", "v2"))


def asof_join(left: pd.DataFrame, right: pd.DataFrame) -> pd.DataFrame:
    return pd.merge_asof(left, right, on="time", by="id")


(df1.groupby("id").cogroup(df2.groupby("id"))
    .applyInPandas(asof_join, "time int, id int, v1 double, v2 string")
    .orderBy("id", "time").show())

# unionAll — снова обычный псевдоним union
print(df.unionAll(df).count())
spark.stop()
