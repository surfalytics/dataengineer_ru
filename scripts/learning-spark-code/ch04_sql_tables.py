"""Глава 4: spark.sql, таблицы и views, Catalog. Данные: 205 рейсов, seed 42, создаём сами."""
import csv
import os
import random
import shutil
import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, desc

os.environ["PYSPARK_PYTHON"] = sys.executable
WH, SRC, EXT = "/tmp/ch04_warehouse", "/tmp/ch04_flights_csv", "/tmp/ch04_unmanaged_flights"
for p in (WH, SRC, EXT):
    shutil.rmtree(p, ignore_errors=True)

spark = (SparkSession.builder.master("local[2]").appName("Ch04Tables")
         .config("spark.ui.enabled", "false")
         .config("spark.sql.warehouse.dir", WH)
         .getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

# Данные: 200 случайных рейсов и 5 рейсов на границах классов задержки
miles = {("SFO", "ORD"): 1846, ("SFO", "JFK"): 2586, ("SFO", "LAX"): 337, ("SFO", "SEA"): 679,
         ("JFK", "LAX"): 2475, ("JFK", "ORD"): 740, ("HNL", "JFK"): 4983, ("HNL", "LAX"): 2556,
         ("ORD", "ATL"): 606, ("ATL", "JFK"): 760}
dist = {tuple(sorted(k)): v for k, v in miles.items()}  # расстояние не зависит от направления
pairs = sorted(dist)
rnd = random.Random(42)
rows = []
for _ in range(200):
    o, d = rnd.choice(pairs)
    if rnd.random() < 0.5:
        o, d = d, o
    date = f"{rnd.randint(1, 3):02d}{rnd.randint(1, 28):02d}{rnd.randint(6, 22):02d}{rnd.choice([0, 15, 30, 45]):02d}"
    rows.append((date, int(rnd.gauss(15, 70)), dist[tuple(sorted((o, d)))], o, d))
for delay in (0, 60, 120, 360, 1638):
    rows.append(("02190925", delay, 1846, "SFO", "ORD"))
os.makedirs(SRC)
with open(f"{SRC}/flights.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["date", "delay", "distance", "origin", "destination"])
    w.writerows(rows)

print("== 1. Чтение со схемой и view ==")
schema = "date STRING, delay INT, distance INT, origin STRING, destination STRING"
df = spark.read.csv(SRC, header=True, schema=schema)
df.createOrReplaceTempView("us_delay_flights_tbl")
inferred = spark.read.csv(SRC, header=True, inferSchema=True)
print("rows:", df.count())
print("date со схемой:", dict(df.dtypes)["date"], "| date через inferSchema:", dict(inferred.dtypes)["date"])

print("== 2. Запросы SQL ==")
spark.sql("""SELECT distance, origin, destination
FROM us_delay_flights_tbl WHERE distance > 1000
ORDER BY distance DESC, origin""").show(3)
spark.sql("""SELECT date, delay, origin, destination
FROM us_delay_flights_tbl
WHERE delay > 120 AND origin = 'SFO' AND destination = 'ORD'
ORDER BY delay DESC, date""").show(3)

spark.sql("""SELECT delay, origin, destination,
CASE
  WHEN delay >= 360 THEN 'Very Long Delays'
  WHEN delay >= 120 THEN 'Long Delays'
  WHEN delay >= 60 THEN 'Short Delays'
  WHEN delay > 0 THEN 'Tolerable Delays'
  WHEN delay = 0 THEN 'No Delays'
  ELSE 'Early'
END AS Flight_Delays
FROM us_delay_flights_tbl""").createOrReplaceTempView("labeled_flights")
spark.sql("""SELECT Flight_Delays, count(*) AS flights FROM labeled_flights
GROUP BY Flight_Delays ORDER BY flights DESC""").show()
spark.sql("""SELECT DISTINCT delay, Flight_Delays FROM labeled_flights
WHERE delay IN (0, 60, 120, 360) ORDER BY delay""").show()

print("== 3. Тот же запрос в DataFrame API ==")
by_sql = spark.sql("""SELECT distance, origin, destination FROM us_delay_flights_tbl
WHERE distance > 1000 ORDER BY distance DESC, origin, destination""")
by_df = (df.select("distance", "origin", "destination")
         .where(col("distance") > 1000)
         .orderBy(desc("distance"), "origin", "destination"))
print("SQL и DataFrame дают одно и то же:", by_sql.collect() == by_df.collect())

print("== 4. База, managed и unmanaged таблицы ==")
spark.sql("CREATE DATABASE learn_spark_db")
spark.sql("USE learn_spark_db")
spark.sql("""CREATE TABLE managed_empty (date STRING, delay INT, distance INT,
origin STRING, destination STRING)""")
df.write.saveAsTable("managed_flights")
spark.sql("""CREATE TABLE unmanaged_csv (date STRING, delay INT, distance INT,
origin STRING, destination STRING)
USING csv OPTIONS (path '/tmp/ch04_flights_csv', header 'true')""")
df.write.option("path", EXT).saveAsTable("unmanaged_flights")
for name in ("managed_empty", "managed_flights", "unmanaged_csv", "unmanaged_flights"):
    print(name, spark.table(name).count())
tables = spark.catalog.listTables()
for t in sorted(tables, key=lambda t: t.name):
    print(f"{t.name:22} {t.tableType:10} temp={t.isTemporary}")

print("== 5. Views ==")
spark.sql("""CREATE OR REPLACE GLOBAL TEMP VIEW us_origin_airport_SFO_global_tmp_view AS
SELECT date, delay, origin, destination FROM managed_flights WHERE origin = 'SFO'""")
df_jfk = spark.sql("""SELECT date, delay, origin, destination FROM managed_flights
WHERE origin = 'JFK'""")
df_jfk.createOrReplaceTempView("us_origin_airport_JFK_tmp_view")
print("global:", spark.sql("SELECT count(*) FROM global_temp.us_origin_airport_SFO_global_tmp_view").first()[0])
print("temp:", spark.read.table("us_origin_airport_JFK_tmp_view").count())

other = spark.newSession()
print("другая сессия, global view:",
      other.sql("SELECT count(*) FROM global_temp.us_origin_airport_SFO_global_tmp_view").first()[0])
spark.sparkContext.setLogLevel("OFF")  # Spark сам пишет ошибку в лог: скроем её
try:
    other.sql("SELECT count(*) FROM us_origin_airport_JFK_tmp_view")
except Exception as e:
    print("другая сессия, temp view:", type(e).__name__, e.getCondition())
spark.sparkContext.setLogLevel("ERROR")

print("== 6. Catalog ==")
print("databases:", sorted(d.name for d in spark.catalog.listDatabases()))
for c in spark.catalog.listColumns("managed_flights"):
    print(c.name, c.dataType, c.nullable)

print("== 7. DROP: managed против unmanaged ==")
managed_dir = f"{WH}/learn_spark_db.db/managed_flights"
print("до DROP: данные managed есть:", os.path.exists(managed_dir),
      "| данные unmanaged есть:", os.path.exists(EXT))
spark.sql("DROP TABLE managed_flights")
spark.sql("DROP TABLE unmanaged_flights")
print("после DROP: данные managed есть:", os.path.exists(managed_dir),
      "| данные unmanaged есть:", os.path.exists(EXT))
print("в Catalog осталось:", sorted(t.name for t in spark.catalog.listTables() if not t.isTemporary))

print("== 8. Кэш и чтение таблицы в DataFrame ==")
spark.sql("CACHE LAZY TABLE unmanaged_csv")
print("в кэше (LAZY, ещё не читали):", spark.catalog.isCached("unmanaged_csv"))
flights_df = spark.table("unmanaged_csv")
same = spark.sql("SELECT * FROM unmanaged_csv")
print("spark.table и spark.sql:", flights_df.count(), same.count())
spark.sql("UNCACHE TABLE unmanaged_csv")
print("после UNCACHE:", spark.catalog.isCached("unmanaged_csv"))
spark.stop()
