"""Глава 5: union, join, window, withColumn, drop, rename, pivot на сгенерированных рейсах."""
import os, sys, random
from pyspark.sql import SparkSession
from pyspark.sql.functions import expr

os.environ["PYSPARK_PYTHON"] = sys.executable

spark = (SparkSession.builder.master("local[2]").appName("Ch05Ops")
         .config("spark.ui.enabled", "false")
         .config("spark.sql.warehouse.dir", "/tmp/ch05-warehouse").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

# Данные: рейсы. date = MMddHHmm, как в книге
rnd = random.Random(42)
cities = ["SEA", "SFO", "JFK", "DEN", "ORD", "LAX", "ATL"]
rows = []
for i in range(3000):
    o, d = rnd.sample(cities, 2)
    month = rnd.choice([1, 2])
    day = rnd.randint(1, 28)
    rows.append((f"{month:02d}{day:02d}{rnd.randint(6, 20):02d}{rnd.choice([0, 30]):02d}",
                 rnd.randint(-10, 120), rnd.choice([590, 602, 1000]), o, d))
# Три рейса SEA -> SFO за 1 января лежат и в общей таблице, и в foo
FOO = [("01010710", 31, 590, "SEA", "SFO"), ("01010955", 104, 590, "SEA", "SFO"),
       ("01010730", 5, 590, "SEA", "SFO")]
rows = [r for r in rows if not (r[3] == "SEA" and r[4] == "SFO" and r[0].startswith("01010"))] + FOO
delays = spark.createDataFrame(rows, "date string, delay int, distance int, origin string, destination string")
delays.createOrReplaceTempView("departureDelays")

airports = spark.createDataFrame(
    [("Seattle", "WA", "USA", "SEA"), ("San Francisco", "CA", "USA", "SFO"),
     ("New York", "NY", "USA", "JFK"), ("Denver", "CO", "USA", "DEN")],
    "City string, State string, Country string, IATA string")
airports.createOrReplaceTempView("airports_na")

# Маленькая таблица foo: три рейса SEA -> SFO за 1 января
foo = spark.createDataFrame(
    FOO,
    "date string, delay int, distance int, origin string, destination string")
foo.createOrReplaceTempView("foo")

print("--- union: строки foo задвоились")
bar = delays.union(foo)
bar.createOrReplaceTempView("bar")
spark.sql("""
    SELECT * FROM bar
    WHERE origin = 'SEA' AND destination = 'SFO' AND date LIKE '01010%' AND delay > 0
    ORDER BY date, delay
""").show()

print("--- join")
spark.sql("""
    SELECT a.City, a.State, f.date, f.delay, f.distance, f.destination
    FROM foo f JOIN airports_na a ON a.IATA = f.origin ORDER BY f.date
""").show()

print("--- window: топ-3 направления по сумме задержек для каждого origin")
spark.sql("""
    SELECT origin, destination, SUM(delay) AS TotalDelays
    FROM departureDelays WHERE origin IN ('SEA', 'SFO', 'JFK')
    GROUP BY origin, destination
""").createOrReplaceTempView("departureDelaysWindow")
spark.sql("""
    SELECT origin, destination, TotalDelays, rank FROM (
        SELECT origin, destination, TotalDelays,
               dense_rank() OVER (PARTITION BY origin ORDER BY TotalDelays DESC) AS rank
        FROM departureDelaysWindow) t
    WHERE rank <= 3 ORDER BY origin, rank
""").show()

print("--- withColumn, drop, withColumnRenamed")
foo2 = foo.withColumn("status", expr("CASE WHEN delay <= 10 THEN 'On-time' ELSE 'Delayed' END"))
foo3 = foo2.drop("delay")
foo4 = foo3.withColumnRenamed("status", "flight_status")
foo4.orderBy("date").show()

print("--- pivot")
spark.sql("""
    SELECT * FROM (
        SELECT destination, CAST(SUBSTRING(date, 0, 2) AS int) AS month, delay
        FROM departureDelays WHERE origin = 'SEA')
    PIVOT (CAST(AVG(delay) AS DECIMAL(4, 2)) AS AvgDelay, MAX(delay) AS MaxDelay
           FOR month IN (1 JAN, 2 FEB))
    ORDER BY destination
""").show()

spark.stop()
