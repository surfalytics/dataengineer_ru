"""Глава 3: типичные операции DataFrame на маленьких «вызовах пожарных» (данные генерируем)."""
import os, sys, random, shutil
from pyspark.sql import SparkSession
from pyspark.sql.types import (StructType, StructField, IntegerType, StringType, FloatType)
import pyspark.sql.functions as F
from pyspark.sql.functions import col, to_timestamp, year

os.environ["PYSPARK_PYTHON"] = sys.executable

spark = (SparkSession.builder.master("local[2]").appName("Ch03Fire")
         .config("spark.ui.enabled", "false").config("spark.ui.showConsoleProgress", "false").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

# Данные: 200 вызовов, фиксированный seed. Даты в виде строк, как в CSV из книги
rnd = random.Random(42)
types = ["Medical Incident", "Medical Incident", "Medical Incident", "Structure Fire",
         "Alarms", "Alarms", "Traffic Collision", "Outside Fire", None]
hoods = ["Mission", "Tenderloin", "SoMa", "Sunset"]
rows = []
for i in range(200):
    y = rnd.choice([2016, 2017, 2018])
    m, d = rnd.randint(1, 12), rnd.randint(1, 28)
    rows.append((1000 + i, rnd.choice(types), f"{m:02d}/{d:02d}/{y}",
                 f"{m:02d}/{d:02d}/{y} {rnd.randint(1, 12):02d}:{rnd.randint(0, 59):02d}:00 PM",
                 rnd.choice(hoods), rnd.randint(1, 3), round(rnd.uniform(1, 12), 1)))

# Схема задана заранее: Spark не читает данные, чтобы угадать типы
fire_schema = StructType([
    StructField("CallNumber", IntegerType(), True),
    StructField("CallType", StringType(), True),
    StructField("CallDate", StringType(), True),
    StructField("AvailableDtTm", StringType(), True),
    StructField("Neighborhood", StringType(), True),
    StructField("NumAlarms", IntegerType(), True),
    StructField("Delay", FloatType(), True),
])
src = "/tmp/ch03_fire_csv"
shutil.rmtree(src, ignore_errors=True)
spark.createDataFrame(rows, fire_schema).write.option("header", True).csv(src)

# Чтение CSV через DataFrameReader с готовой схемой
fire_df = spark.read.csv(src, header=True, schema=fire_schema)
print("rows:", fire_df.count())

# Projections и filters
(fire_df.select("CallNumber", "CallType").where(col("CallType") != "Medical Incident")
 .orderBy("CallNumber").show(3))

# Сколько разных типов вызовов
(fire_df.select("CallType").where(col("CallType").isNotNull())
 .agg(F.countDistinct("CallType").alias("DistinctCallTypes")).show())

# Переименовали колонку, строки -> timestamp, старые колонки убрали
new_df = fire_df.withColumnRenamed("Delay", "ResponseDelayedinMins")
ts_df = (new_df
         .withColumn("IncidentDate", to_timestamp(col("CallDate"), "MM/dd/yyyy"))
         .drop("CallDate")
         .withColumn("AvailableDtTS", to_timestamp(col("AvailableDtTm"), "MM/dd/yyyy hh:mm:ss a"))
         .drop("AvailableDtTm"))
ts_df.select("CallNumber", "IncidentDate", "AvailableDtTS").orderBy("CallNumber").show(3, False)
ts_df.select(year("IncidentDate").alias("year")).distinct().orderBy("year").show()

# Агрегации: самые частые типы
(ts_df.where(col("CallType").isNotNull()).groupBy("CallType").count()
 .orderBy(col("count").desc(), "CallType").show(truncate=False))

# Статистика одной строкой
ts_df.select(F.sum("NumAlarms").alias("alarms"),
             F.round(F.avg("ResponseDelayedinMins"), 2).alias("avg_delay"),
             F.min("ResponseDelayedinMins").alias("min_delay"),
             F.max("ResponseDelayedinMins").alias("max_delay")).show()

# Parquet хранит схему: при чтении её задавать не нужно
pq = "/tmp/ch03_fire_parquet"
shutil.rmtree(pq, ignore_errors=True)
ts_df.write.format("parquet").save(pq)
spark.read.parquet(pq).printSchema()
spark.stop()
