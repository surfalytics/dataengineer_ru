"""Глава 11: потоковые прогнозы. Те же transform(), но данные идут через readStream."""
import os, shutil, sys
import numpy as np
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression

os.environ["PYSPARK_PYTHON"] = sys.executable
spark = (SparkSession.builder.master("local[2]").appName("ch11-stream")
         .config("spark.ui.enabled", "false").config("spark.sql.shuffle.partitions", "2")
         .config("spark.sql.execution.arrow.pyspark.enabled", "false").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

rng = np.random.default_rng(7)
def make(n):
    pdf = pd.DataFrame({"bedrooms": rng.integers(1, 5, n).astype(float),
                        "accommodates": rng.integers(1, 9, n).astype(float)})
    pdf["price"] = 50 + 40 * pdf["bedrooms"] + 10 * pdf["accommodates"] + rng.normal(0, 5, n)
    return pdf

# Обучаем маленькую модель
train = spark.createDataFrame(make(300))
model = Pipeline(stages=[VectorAssembler(inputCols=["bedrooms", "accommodates"], outputCol="features"),
                         LinearRegression(labelCol="price")]).fit(train)

# Имитация потока: 4 маленьких parquet-файла в одной папке
src = "/tmp/ch11-stream-in"
shutil.rmtree(src, ignore_errors=True)
for i in range(4):
    spark.createDataFrame(make(25)).coalesce(1).write.mode("append").parquet(src)
schema = spark.read.parquet(src).schema   # у потока схема задаётся заранее

stream = (spark.readStream.schema(schema).option("maxFilesPerTrigger", 1).parquet(src))
pred = model.transform(stream)            # тот же transform(), что и в batch

def show_batch(df, batch_id):
    r = df.agg({"prediction": "avg", "price": "avg"}).first()
    print(f"batch {batch_id}: rows={df.count()}, avg pred={r['avg(prediction)']:.0f}")

q = (pred.writeStream.foreachBatch(show_batch)
     .option("checkpointLocation", "/tmp/ch11-stream-ckpt")
     .trigger(availableNow=True).start())
q.awaitTermination()
spark.stop()
