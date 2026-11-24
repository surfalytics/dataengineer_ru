"""Глава 5: UDF для Spark SQL, проверка null и pandas UDF."""
import os, sys
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, pandas_udf
from pyspark.sql.types import LongType

os.environ["PYSPARK_PYTHON"] = sys.executable

spark = (SparkSession.builder.master("local[2]").appName("Ch05Udf")
         .config("spark.ui.enabled", "false")
         .config("spark.sql.warehouse.dir", "/tmp/ch05-warehouse").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

# 1. Обычная UDF: регистрируем в сессии и зовём из SQL
def cubed(s):
    return s * s * s

spark.udf.register("cubed", cubed, LongType())
spark.range(1, 9).createOrReplaceTempView("udf_test")
print("--- SQL UDF")
spark.sql("SELECT id, cubed(id) AS id_cubed FROM udf_test ORDER BY id").show()

# 2. Null внутри UDF: сами проверяем None и возвращаем None
def strlen_safe(s):
    return None if s is None else len(s)

spark.udf.register("strlen_safe", strlen_safe, "int")
spark.createDataFrame([("spark",), (None,), ("a",)], "s string").createOrReplaceTempView("test1")
print("--- UDF с проверкой null")
spark.sql("""
    SELECT s, strlen_safe(s) AS len_in_udf,
           CASE WHEN s IS NOT NULL THEN strlen_safe(s) END AS len_in_case
    FROM test1 ORDER BY s
""").show()

# 3. pandas UDF: функция работает с целой pandas.Series
def cubed_pd(a: pd.Series) -> pd.Series:
    return a * a * a

cubed_udf = pandas_udf(cubed_pd, returnType=LongType())

print("--- Локальная pandas-функция (только на driver)")
print(cubed_pd(pd.Series([1, 2, 3])))

print("--- pandas UDF в Spark")
spark.range(1, 4).select("id", cubed_udf(col("id")).alias("cubed")).orderBy("id").show()

spark.stop()
