"""Глава 9: Delta Lake на Spark. Запись, поток, схема, UPDATE/DELETE/MERGE, история, time travel.
Запуск (образ с Delta): SPARK_IMAGE=learning-spark:4.2.0-delta scripts/learning-spark-code/spark-python scripts/learning-spark-code/ch09_delta.py"""
# runner-env: SPARK_IMAGE=learning-spark:4.2.0-delta
import shutil, tempfile, os, sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit
from delta import configure_spark_with_delta_pip, DeltaTable

os.environ["PYSPARK_PYTHON"] = sys.executable
builder = (SparkSession.builder.master("local[2]").appName("delta")
           .config("spark.ui.enabled", "false")
           .config("spark.sql.shuffle.partitions", 2)
           .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
           .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog"))
spark = configure_spark_with_delta_pip(builder).getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

base = tempfile.mkdtemp(dir="/tmp")
parquet_path, delta_path = base + "/loans_parquet", base + "/loans_delta"
stream_src, ckpt = base + "/stream_src", base + "/ckpt"

# Данные займов: 10 строк, детерминированно
loans = [(i, 1000 + 500 * (i % 3), float([1000, 250, 1500, 0, 750][i % 5]),
          ["CA", "OR", "WA", "TX", "OR"][i % 5]) for i in range(10)]
cols = ["loan_id", "funded_amnt", "paid_amnt", "addr_state"]
df = spark.createDataFrame(loans, cols).withColumn("funded_amnt", col("funded_amnt").cast("int"))
df.write.format("parquet").save(parquet_path)

# 1. Parquet -> Delta: меняем только format
spark.read.format("parquet").load(parquet_path).write.format("delta").save(delta_path)
spark.read.format("delta").load(delta_path).createOrReplaceTempView("loans_delta")
print("rows:", spark.sql("SELECT count(*) FROM loans_delta").first()[0])

# 2. Поток дописывает в ту же таблицу, пока пакетная запись тоже возможна
new = spark.createDataFrame([(100, 2000, 500.0, "CA"), (101, 2000, 0.0, "TX")], cols) \
    .withColumn("funded_amnt", col("funded_amnt").cast("int"))
new.write.format("parquet").save(stream_src)
stream_df = spark.readStream.schema(df.schema).format("parquet").load(stream_src)
q = (stream_df.writeStream.format("delta").option("checkpointLocation", ckpt)
     .trigger(availableNow=True).start(delta_path))
q.awaitTermination()
print("rows after stream:", spark.read.format("delta").load(delta_path).count())

# 3. Запись с лишней колонкой отклоняется
upd_cols = cols + ["closed"]
loan_updates = (spark.createDataFrame([(1111111, 1000, 1000.0, "TX", True),
                                       (2222222, 2000, 0.0, "CA", False)], upd_cols)
                .withColumn("funded_amnt", col("funded_amnt").cast("int")))
try:
    loan_updates.write.format("delta").mode("append").save(delta_path)
except Exception as e:
    print("append with new column failed:", type(e).__name__)

# 4. mergeSchema: колонка добавляется, старые строки получают NULL
loan_updates.write.format("delta").mode("append").option("mergeSchema", "true").save(delta_path)
t = spark.read.format("delta").load(delta_path)
print("columns:", t.columns)
print("closed IS NULL:", t.filter("closed IS NULL").count(), "of", t.count())

# 5. UPDATE: исправляем OR на WA
dt = DeltaTable.forPath(spark, delta_path)
dt.update("addr_state = 'OR'", {"addr_state": "'WA'"})
print("OR left:", spark.read.format("delta").load(delta_path).filter("addr_state = 'OR'").count())

# 6. DELETE: удаляем полностью оплаченные займы
dt.delete("funded_amnt <= paid_amnt")
print("rows after delete:", spark.read.format("delta").load(delta_path).count())

# 7. MERGE: upsert (новые строки + обновление существующей)
changes = spark.createDataFrame([(1, 1500, 999.0, "NY", False), (555, 3000, 10.0, "FL", False)], upd_cols) \
    .withColumn("funded_amnt", col("funded_amnt").cast("int"))
(dt.alias("t").merge(changes.alias("s"), "t.loan_id = s.loan_id")
 .whenMatchedUpdateAll().whenNotMatchedInsertAll().execute())
print("loan 1:", spark.read.format("delta").load(delta_path).filter("loan_id = 1").first().asDict())

# 8. Insert-only merge: дедупликация при дозагрузке истории
hist = spark.createDataFrame([(1, 9999, 0.0, "AA", False), (777, 500, 0.0, "NV", False)], upd_cols) \
    .withColumn("funded_amnt", col("funded_amnt").cast("int"))
(dt.alias("t").merge(hist.alias("s"), "t.loan_id = s.loan_id")
 .whenNotMatchedInsertAll().execute())
now = spark.read.format("delta").load(delta_path)
print("loan 1 still:", now.filter("loan_id = 1").first()["addr_state"],
      "| loan 777 added:", now.filter("loan_id = 777").count())

# 9. История операций
for r in dt.history().select("version", "operation").orderBy("version").collect():
    print("v%d %s" % (r["version"], r["operation"]))

# 10. Time travel
v0 = spark.read.format("delta").option("versionAsOf", 0).load(delta_path)
print("v0 rows:", v0.count(), "| columns:", v0.columns)
print("now rows:", now.count())
shutil.rmtree(base)
