"""Глава 3: один и тот же запрос на DataFrame и в SQL проходит через Catalyst. Смотрим explain."""
import os, sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import count, sum as sum_

os.environ["PYSPARK_PYTHON"] = sys.executable

spark = (SparkSession.builder.master("local[2]").appName("Ch03Catalyst")
         .config("spark.ui.enabled", "false").config("spark.ui.showConsoleProgress", "false")
         .config("spark.sql.shuffle.partitions", 4)
         .config("spark.sql.adaptive.enabled", "false").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

rows = [("CA", "Red", 10), ("CA", "Red", 5), ("CA", "Blue", 7),
        ("TX", "Red", 3), ("TX", "Green", 8), ("TX", "Green", 2)]
mnm = spark.createDataFrame(rows, ["State", "Color", "Count"])
mnm.createOrReplaceTempView("mnm")

q_df = (mnm.select("State", "Color", "Count").groupBy("State", "Color")
        .agg(sum_("Count").alias("Total")).orderBy("Total", ascending=False))
q_sql = spark.sql("""SELECT State, Color, sum(Count) AS Total
                     FROM mnm GROUP BY State, Color ORDER BY Total DESC""")
q_df.show()

# Четыре фазы: Parsed -> Analyzed -> Optimized -> Physical
q_df.explain("extended")

# Тот же запрос в SQL даёт тот же физический план?
def physical(q):
    return q._jdf.queryExecution().executedPlan().toString()
import re
norm = lambda s: re.sub(r"plan_id=\d+", "", re.sub(r"#\d+L?", "#", s))
print("same physical plan:", norm(physical(q_df)) == norm(physical(q_sql)))

# Predicate pushdown: фильтр после join уходит ниже, к источнику
users = spark.createDataFrame([(1, "a"), (2, "b")], ["id", "name"])
events = spark.createDataFrame([(1, "2014-05-01"), (2, "2016-03-01")], ["uid", "date"])
joined = users.join(events, users.id == events.uid).filter(events.date > "2015-01-01")
joined.explain()
spark.stop()
