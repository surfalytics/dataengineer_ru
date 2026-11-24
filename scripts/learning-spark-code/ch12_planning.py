"""Глава 12: dynamic partition pruning, AQE, join hints, explain."""
import io, re, shutil, sys
from contextlib import redirect_stdout
from pyspark.sql import SparkSession

spark = (SparkSession.builder.master("local[2]").appName("ch12-planning")
         .config("spark.ui.enabled", "false")
         .config("spark.sql.shuffle.partitions", "50")
         .getOrCreate())
spark.sparkContext.setLogLevel("ERROR")


def plan(df, mode="formatted"):
    buf = io.StringIO()
    with redirect_stdout(buf):
        df.explain(mode=mode)
    return buf.getvalue()


# --- Dynamic partition pruning ---
path = "/tmp/ch12_sales"
shutil.rmtree(path, ignore_errors=True)
sales = spark.range(0, 3000).selectExpr(
    "id AS order_id",
    "date_add(DATE'2026-01-01', CAST(id % 30 AS INT)) AS sale_date",
    "CAST(id % 7 AS INT) AS amount")
sales.write.partitionBy("sale_date").parquet(path)
fact = spark.read.parquet(path)
fact.createOrReplaceTempView("sales")
spark.sql("""SELECT sale_date, (dayofweek(sale_date) IN (1, 7)) AS is_weekend
             FROM (SELECT DISTINCT sale_date FROM sales)""").createOrReplaceTempView("dim_date")

q = """SELECT count(*) AS n, sum(s.amount) AS total
       FROM sales s JOIN dim_date d ON s.sale_date = d.sale_date
       WHERE d.is_weekend"""
for flag in ("true", "false"):
    spark.conf.set("spark.sql.optimizer.dynamicPartitionPruning.enabled", flag)
    text = plan(spark.sql(q))
    print(f"DPP={flag}: dynamicpruning in plan = {'dynamicpruning' in text}")
spark.conf.set("spark.sql.optimizer.dynamicPartitionPruning.enabled", "true")
spark.sql(q).show()

# --- Adaptive Query Execution ---
for key in ("spark.sql.adaptive.enabled",
            "spark.sql.adaptive.coalescePartitions.enabled",
            "spark.sql.adaptive.skewJoin.enabled"):
    print(key, "=", spark.conf.get(key))

agg = spark.range(0, 100000).selectExpr("id % 10 AS k").groupBy("k").count().orderBy("k")
before = plan(agg, "simple")
agg.collect()  # запуск: AQE меняет план на лету
final = plan(agg, "simple")
print("до запуска: isFinalPlan=false:", "isFinalPlan=false" in before)
print("после запуска: coalesced:", "coalesced" in final)

# --- Join hints ---
spark.range(1000).selectExpr("id AS key", "id AS x").createOrReplaceTempView("a")
spark.range(1000).selectExpr("id AS key", "id AS y").createOrReplaceTempView("b")
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")  # без подсказки broadcast не нужен
for hint in ("MERGE", "BROADCAST", "SHUFFLE_HASH", "SHUFFLE_REPLICATE_NL"):
    t = plan(spark.sql(f"SELECT /*+ {hint}(a) */ a.key FROM a JOIN b ON a.key = b.key"), "simple")
    join = re.search(r"(SortMergeJoin|BroadcastHashJoin|ShuffledHashJoin|CartesianProduct|BroadcastNestedLoopJoin)", t)
    print(f"{hint:22s} -> {join.group(1) if join else '?'}")

# --- explain: режимы ---
print(plan(spark.range(10).filter("id > 5").select("id")))
spark.stop()
