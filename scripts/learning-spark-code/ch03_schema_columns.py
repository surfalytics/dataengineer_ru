"""Глава 3: RDD против DataFrame, схема в DDL, колонки, выражения, Row."""
import os, sys
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import avg, col, expr, concat

os.environ["PYSPARK_PYTHON"] = sys.executable

spark = (SparkSession.builder.master("local[2]").appName("Ch03Schema")
         .config("spark.ui.enabled", "false").config("spark.ui.showConsoleProgress", "false").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")
sc = spark.sparkContext

pairs = [("Brooke", 20), ("Denny", 31), ("Jules", 30), ("TD", 35), ("Brooke", 25)]

# 1. RDD: мы говорим Spark, КАК считать. Для Spark это непрозрачные lambda
ages_rdd = (sc.parallelize(pairs)
            .map(lambda x: (x[0], (x[1], 1)))
            .reduceByKey(lambda x, y: (x[0] + y[0], x[1] + y[1]))
            .map(lambda x: (x[0], x[1][0] / x[1][1])))
print("RDD:", sorted(ages_rdd.collect()))

# 2. DataFrame: мы говорим, ЧТО нужно. Spark видит намерение
data_df = spark.createDataFrame(pairs, ["name", "age"])
data_df.groupBy("name").agg(avg("age")).orderBy("name").show()

# 3. Схема в виде DDL-строки
schema = "Id INT, First STRING, Last STRING, Hits INT, Campaigns ARRAY<STRING>"
data = [
    (1, "Jules", "Damji", 4535, ["twitter", "LinkedIn"]),
    (2, "Brooke", "Wenig", 8908, ["twitter", "LinkedIn"]),
    (3, "Denny", "Lee", 7659, ["web", "twitter", "FB", "LinkedIn"]),
    (4, "Tathagata", "Das", 10568, ["twitter", "FB"]),
    (5, "Matei", "Zaharia", 40578, ["web", "twitter", "FB", "LinkedIn"]),
    (6, "Reynold", "Xin", 25568, ["twitter", "LinkedIn"]),
]
blogs_df = spark.createDataFrame(data, schema)
blogs_df.printSchema()

# 4. Колонки и выражения
blogs_df.select(expr("Hits * 2").alias("hits_x2")).show(2)
(blogs_df.withColumn("Big Hitters", expr("Hits > 10000"))
 .select("Id", "Hits", "Big Hitters").show())
(blogs_df.withColumn("AuthorsId", concat(col("First"), col("Last"), col("Id")))
 .select("AuthorsId").show(3))
blogs_df.sort(col("Id").desc()).select("Id", "First").show(3)

# 5. Row
row = Row(6, "Reynold", "Xin")
print("row[1] =", row[1])
authors = spark.createDataFrame([Row("Matei Zaharia", "CA"), Row("Reynold Xin", "CA")],
                                ["Author", "State"])
authors.show()
spark.stop()
