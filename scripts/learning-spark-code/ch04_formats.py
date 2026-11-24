"""Глава 4: встроенные источники данных: Parquet, JSON, CSV, ORC, binaryFile, image. Данные создаём сами."""
import os
import re
import shutil
import struct
import sys
import zlib

from pyspark.sql import SparkSession

os.environ["PYSPARK_PYTHON"] = sys.executable
BASE = "/tmp/ch04_formats"
shutil.rmtree(BASE, ignore_errors=True)
os.makedirs(BASE)

spark = (SparkSession.builder.master("local[2]").appName("Ch04Formats")
         .config("spark.ui.enabled", "false").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")


def ls(path):
    """Имена файлов в папке без служебных .crc, с коротким именем вместо uuid."""
    names = sorted(f for f in os.listdir(path) if not f.startswith("."))
    return [re.sub(r"part-(\d+)-[0-9a-f-]{36}-c000", r"part-\1-<uuid>-c000", f) for f in names]


# Данные: перелёты между странами, как в сводках из книги
rows = [("United States", "Romania", 1), ("United States", "Ireland", 264), ("United States", "India", 69),
        ("Egypt", "United States", 24), ("Equatorial Guinea", "United States", 1),
        ("United States", "Singapore", 25), ("United States", "Grenada", 54), ("Costa Rica", "United States", 477),
        ("Senegal", "United States", 29), ("Moldova", "United States", 1)]
schema = "DEST_COUNTRY_NAME STRING, ORIGIN_COUNTRY_NAME STRING, count INT"
df = spark.createDataFrame(rows, schema).coalesce(1)

print("== 1. Parquet ==")
pq = f"{BASE}/parquet"
(df.write.format("parquet")
 .mode("overwrite")
 .option("compression", "snappy")
 .save(pq))
print(ls(pq))
parquet_df = spark.read.format("parquet").load(pq)
print(parquet_df.dtypes)
spark.sql(f"""CREATE OR REPLACE TEMPORARY VIEW us_delay_flights_tbl
USING parquet OPTIONS (path "{pq}")""")
spark.sql("SELECT * FROM us_delay_flights_tbl ORDER BY count DESC, ORIGIN_COUNTRY_NAME").show(3, truncate=False)

print("== 2. Режимы записи ==")
try:
    df.write.format("parquet").save(pq)
except Exception as e:
    print("по умолчанию:", type(e).__name__, e.getCondition())
df.write.format("parquet").mode("append").save(pq)
print("append:", spark.read.parquet(pq).count())
df.write.format("parquet").mode("ignore").save(pq)
print("ignore:", spark.read.parquet(pq).count())
df.write.format("parquet").mode("overwrite").save(pq)
print("overwrite:", spark.read.parquet(pq).count())

print("== 3. JSON ==")
js = f"{BASE}/json"
df.write.format("json").mode("overwrite").save(js)
first = open(f"{js}/" + [f for f in os.listdir(js) if f.endswith(".json")][0]).readline().strip()
print(first)
print(spark.read.format("json").load(js).orderBy("count").first().asDict())
os.makedirs(f"{BASE}/multi")
with open(f"{BASE}/multi/data.json", "w") as f:
    f.write('[\n  {"DEST_COUNTRY_NAME": "Egypt", "count": 24},\n  {"DEST_COUNTRY_NAME": "Senegal", "count": 29}\n]\n')
print("без multiLine:", spark.read.json(f"{BASE}/multi").columns)
print("с multiLine:", spark.read.option("multiLine", "true").json(f"{BASE}/multi").columns)

print("== 4. CSV ==")
cs = f"{BASE}/csv"
os.makedirs(cs)
with open(f"{cs}/flights.csv", "w") as f:
    f.write("DEST_COUNTRY_NAME,ORIGIN_COUNTRY_NAME,count\nEgypt,United States,24\nSenegal,United States,\n"
            "Moldova,United States,abc\nGrenada,United States,54\n")
for mode in ("PERMISSIVE", "DROPMALFORMED"):
    d = (spark.read.format("csv").schema(schema).option("header", "true")
         .option("mode", mode).option("nullValue", "").load(cs))
    print(mode, [tuple(r) for r in d.orderBy("DEST_COUNTRY_NAME").collect()])
spark.sparkContext.setLogLevel("OFF")  # Spark сам пишет в лог трассу ошибки: скроем её
try:
    (spark.read.format("csv").schema(schema).option("header", "true")
     .option("mode", "FAILFAST").load(cs).collect())
except Exception as e:
    print("FAILFAST:", re.search(r"\[([A-Z_.]+)\]", str(e)).group(1))
spark.sparkContext.setLogLevel("ERROR")
out = f"{BASE}/csv_out"
df.write.format("csv").option("header", "true").mode("overwrite").save(out)
print(ls(out))

print("== 5. ORC и partitionBy ==")
orc = f"{BASE}/orc"
df.write.format("orc").mode("overwrite").option("compression", "snappy").save(orc)
print(ls(orc))
print(spark.read.format("orc").load(orc).count())
part = f"{BASE}/by_origin"
df.write.partitionBy("ORIGIN_COUNTRY_NAME").mode("overwrite").parquet(part)
print(ls(part)[:4], "...", len(ls(part)))
print(spark.read.parquet(part).columns)
print(spark.read.parquet(f"{part}/ORIGIN_COUNTRY_NAME=Ireland").columns)


def png(r, g, b):
    """Картинка PNG 2x2 одного цвета, собранная вручную."""
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
    raw = b"".join(b"\x00" + bytes([r, g, b]) * 2 for _ in range(2))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


print("== 6. image и binaryFile ==")
imgs = f"{BASE}/images"
for label, color in ((0, (255, 0, 0)), (1, (0, 255, 0))):
    os.makedirs(f"{imgs}/label={label}")
    for i in range(2):
        with open(f"{imgs}/label={label}/img{i}.png", "wb") as f:
            f.write(png(*color))
with open(f"{imgs}/label=0/notes.txt", "w") as f:
    f.write("не картинка")

images_df = spark.read.format("image").option("dropInvalid", "true").load(imgs)
images_df.select("image.height", "image.width", "image.nChannels", "image.mode", "label").orderBy("label").show()

binary_df = (spark.read.format("binaryFile")
             .option("pathGlobFilter", "*.png")
             .load(imgs))
print(binary_df.columns)
binary_df.selectExpr("length", "label").orderBy("label").show()
binary_rec = (spark.read.format("binaryFile")
              .option("pathGlobFilter", "*.png")
              .option("recursiveFileLookup", "true")
              .load(imgs))
print("с recursiveFileLookup:", binary_rec.columns)
spark.stop()
