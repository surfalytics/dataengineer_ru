"""Глава 7: cache, persist, unpersist и CACHE TABLE."""
import os, sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.storagelevel import StorageLevel

os.environ["PYSPARK_PYTHON"] = sys.executable

spark = (SparkSession.builder.master("local[2]").appName("cache")
         .config("spark.ui.enabled", "false").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

df = spark.range(1_000_000).toDF("id").withColumn("square", col("id") * col("id"))

print("до cache:", df.is_cached, df.storageLevel)

# cache() ленивый: данные попадут в память после первого action
df.cache()
print("после cache(), до action:", df.is_cached)
print("count (кладёт в кэш):", df.count())
print("count (читает из кэша):", df.count())
print("уровень по умолчанию:", df.storageLevel)

# unpersist снимает кэш
df.unpersist()
print("после unpersist:", df.is_cached)

# persist: свой уровень хранения
df.persist(StorageLevel.DISK_ONLY)
print("count:", df.count())
print("DISK_ONLY:", df.storageLevel)
df.unpersist()

# Кэш для таблицы: имя видно в Spark UI
df.createOrReplaceTempView("df_table")
spark.sql("CACHE TABLE df_table")
print("таблица в кэше:", spark.catalog.isCached("df_table"))
spark.sql("SELECT count(*) AS cnt FROM df_table").show()
spark.sql("UNCACHE TABLE df_table")
print("таблица в кэше после UNCACHE:", spark.catalog.isCached("df_table"))
spark.stop()
