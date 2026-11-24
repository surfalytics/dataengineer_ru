"""Глава 8: stream-static join и stream-stream join (inner и left outer) с watermark."""
import json, os, pathlib, shutil, sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr, date_format, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType

os.environ["PYSPARK_PYTHON"] = sys.executable
spark = (SparkSession.builder.master("local[2]").appName("ch08-joins")
         .config("spark.ui.enabled", "false")
         .config("spark.sql.session.timeZone", "UTC")
         .config("spark.sql.shuffle.partitions", 2).getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

base = pathlib.Path("/tmp/ch08_join")
shutil.rmtree(base, ignore_errors=True)

def write_files(folder, key, batches):
    d = base / folder
    d.mkdir(parents=True)
    for i, rows in enumerate(batches):
        f = d / f"b{i}.json"
        f.write_text("".join(json.dumps({"adId": a, key: f"2026-01-01 {t}:00"}) + "\n" for a, t in rows))
        os.utime(f, (1_000_000 + i, 1_000_000 + i))

write_files("impressions", "impressionTime",
            [[("a1", "12:00"), ("a2", "12:05")], [("a3", "13:00")], [("a4", "15:00")], [("a5", "18:00")]])
write_files("clicks", "clickTime",
            [[("a1", "12:20")], [("a3", "13:30")], [("a4", "15:20")], [("a5", "18:10")]])

def stream(folder, key):
    schema = StructType([StructField("adId", StringType()), StructField(key, StringType())])
    return (spark.readStream.schema(schema).option("maxFilesPerTrigger", 1).json(str(base / folder))
            .withColumn(key, to_timestamp(key)))

def hhmm(c):
    return date_format(col(c), "HH:mm").alias(c)

# 1. stream-static: потоку кликов нужен справочник рекламодателей (статичная таблица)
advertisers = spark.createDataFrame([("a1", "Acme"), ("a2", "Acme"), ("a3", "Globex"),
                                     ("a4", "Initech"), ("a5", "Globex")], ["adId", "advertiser"])
def show_static(df, batch_id):
    rows = df.select("adId", hhmm("clickTime"), "advertiser").orderBy("adId").collect()
    print(f"batch {batch_id}:", "; ".join(f"{r.adId} {r.clickTime} {r.advertiser}" for r in rows) or "-")

print("=== stream-static join: обогащаем клики")
(stream("clicks", "clickTime").join(advertisers, "adId").writeStream
    .foreachBatch(show_static).option("checkpointLocation", str(base / "ck_static"))
    .trigger(availableNow=True).start().awaitTermination())

# 2. stream-stream: watermark на обоих входах и условие по времени
impressions = (stream("impressions", "impressionTime")
               .selectExpr("adId AS impressionAdId", "impressionTime")
               .withWatermark("impressionTime", "2 hours"))
clicks = (stream("clicks", "clickTime")
          .selectExpr("adId AS clickAdId", "clickTime")
          .withWatermark("clickTime", "3 hours"))
cond = expr("""clickAdId = impressionAdId AND
               clickTime BETWEEN impressionTime AND impressionTime + interval 1 hour""")

def show_join(df, batch_id):
    rows = (df.select("impressionAdId", hhmm("impressionTime"), "clickAdId", hhmm("clickTime"))
              .orderBy("impressionAdId").collect())
    print(f"batch {batch_id}:", "; ".join(
        f"impression {r.impressionAdId}@{r.impressionTime} + click {r.clickAdId}@{r.clickTime}" for r in rows) or "-")

for kind in ("inner", "leftOuter"):
    print(f"=== stream-stream join: {kind}")
    (impressions.join(clicks, cond, kind).writeStream
        .foreachBatch(show_join).option("checkpointLocation", str(base / f"ck_{kind}"))
        .trigger(availableNow=True).start().awaitTermination())
spark.stop()
