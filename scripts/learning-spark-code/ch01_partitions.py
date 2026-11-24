"""Глава 1: данные делятся на partition, каждый task берёт одну."""
import os, sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import spark_partition_id

# worker использует тот же Python, что и driver
os.environ["PYSPARK_PYTHON"] = sys.executable

spark = (SparkSession.builder.master("local[2]").appName("partitions")
         .config("spark.ui.enabled", "false").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

# 10 000 чисел сразу в 8 partition
df = spark.range(0, 10000, 1, 8)
print("range partitions:", df.rdd.getNumPartitions())

# repartition(8) для уже готового DataFrame (в книге так читают большой файл)
log_df = spark.createDataFrame([(i, f"line {i}") for i in range(1000)], ["id", "text"]).repartition(8)
print("repartition partitions:", log_df.rdd.getNumPartitions())

# Сколько строк в каждой partition
df.groupBy(spark_partition_id().alias("partition")).count().orderBy("partition").show()
spark.stop()
