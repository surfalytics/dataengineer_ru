"""Глава 8: окна по event time, watermark и режимы вывода update / append."""
import json, os, pathlib, shutil, sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window, date_format, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

os.environ["PYSPARK_PYTHON"] = sys.executable
spark = (SparkSession.builder.master("local[2]").appName("ch08-windows")
         .config("spark.ui.enabled", "false")
         .config("spark.sql.session.timeZone", "UTC")
         .config("spark.sql.shuffle.partitions", 2).getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

base = pathlib.Path("/tmp/ch08_win")
shutil.rmtree(base, ignore_errors=True)
src = base / "in"
src.mkdir(parents=True)

# Каждый файл - один micro-batch. События приходят не по порядку event time.
batches = [
    [("12:07", "id1"), ("12:08", "id2")],
    [("12:11", "id1"), ("12:15", "id1")],
    [("12:13", "id3"), ("11:30", "id1")],   # 12:13 опоздало, но принято; 11:30 слишком старое
    [("12:30", "id2")],
    [("12:31", "id1")],
]
for i, rows in enumerate(batches):
    f = src / f"batch{i}.json"
    f.write_text("".join(json.dumps({"eventTime": f"2026-01-01 {t}:00", "sensorId": s}) + "\n"
                         for t, s in rows))
    os.utime(f, (1_000_000 + i, 1_000_000 + i))     # порядок файлов фиксирован

schema = StructType([StructField("eventTime", StringType()), StructField("sensorId", StringType())])
readings = (spark.readStream.schema(schema).option("maxFilesPerTrigger", 1).json(str(src))
            .withColumn("eventTime", to_timestamp("eventTime")))

def counts_for(df):
    return (df.withWatermark("eventTime", "10 minutes")
              .groupBy("sensorId", window("eventTime", "5 minutes"))
              .count())

def show_batch(df, batch_id):
    rows = (df.select("sensorId", date_format(col("window.start"), "HH:mm").alias("start"),
                      date_format(col("window.end"), "HH:mm").alias("end"), "count")
              .orderBy("start", "sensorId").collect())
    print(f"batch {batch_id}:", "; ".join(f"{r.sensorId} {r.start}-{r.end} = {r['count']}" for r in rows) or "-")

def run(mode, ckpt):
    q = (counts_for(readings).writeStream.foreachBatch(show_batch).outputMode(mode)
         .option("checkpointLocation", str(base / ckpt))
         .trigger(availableNow=True).start())
    q.awaitTermination()

print("=== update, окно 5 минут, watermark 10 минут")
run("update", "ck_update")
print("=== append: окно выводится один раз, когда watermark его закрыл")
run("append", "ck_append")

# Скользящее окно: 10 минут с шагом 5. Одно событие попадает в два окна.
one = spark.createDataFrame([("2026-01-01 12:07:00", "id1")], ["t", "sensorId"]) \
           .withColumn("t", to_timestamp("t"))
print("=== окно 10 минут, шаг 5: событие 12:07 попадает в два окна")
rows = (one.groupBy("sensorId", window("t", "10 minutes", "5 minutes")).count()
        .select("sensorId", date_format(col("window.start"), "HH:mm").alias("start"),
                date_format(col("window.end"), "HH:mm").alias("end"), "count")
        .orderBy("start").collect())
for r in rows:
    print(r.sensorId, f"{r.start}-{r.end}", r["count"])
spark.stop()
