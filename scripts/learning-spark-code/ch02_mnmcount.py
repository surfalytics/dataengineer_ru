import csv
import random

from pyspark.sql import SparkSession
from pyspark.sql.functions import count

# Данные: 20 000 строк <State, Color, Count>, фиксированный seed
random.seed(42)
states = ["CA", "WA", "OR", "TX", "CO", "NV", "AZ", "UT", "NM", "WY"]
colors = ["Yellow", "Green", "Brown", "Orange", "Red", "Blue"]
with open("/tmp/mnm_dataset.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["State", "Color", "Count"])
    for _ in range(20000):
        state = random.choice(states)
        weights = [3, 1, 1, 1, 1, 1] if state == "CA" else [1] * 6  # в CA любят Yellow
        w.writerow([state, random.choices(colors, weights)[0], random.randint(1, 100)])

spark = (SparkSession.builder.master("local[2]").appName("PythonMnMCount")
         .config("spark.ui.enabled", "false").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

mnm_df = (spark.read.format("csv")
          .option("header", "true")
          .option("inferSchema", "true")
          .load("/tmp/mnm_dataset.csv"))

count_mnm_df = (mnm_df
                .select("State", "Color", "Count")
                .groupBy("State", "Color")
                .agg(count("Count").alias("Total"))
                .orderBy("Total", "State", "Color", ascending=[False, True, True]))
count_mnm_df.show(n=5, truncate=False)
print("Total Rows = %d" % count_mnm_df.count())

ca_count_mnm_df = (mnm_df
                   .select("State", "Color", "Count")
                   .where(mnm_df.State == "CA")
                   .groupBy("State", "Color")
                   .agg(count("Count").alias("Total"))
                   .orderBy("Total", "Color", ascending=[False, True]))
ca_count_mnm_df.show(n=10, truncate=False)
spark.stop()
