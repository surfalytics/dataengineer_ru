"""Глава 6: типизированный Dataset есть только в Scala и Java. В PySpark тот же урок
показывает разница между встроенными выражениями (DSL) и своей функцией (UDF):
Catalyst видит выражение и не видит функцию."""
import contextlib, io, os, random, re, sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, desc, when, udf
from pyspark.sql.types import BooleanType

os.environ["PYSPARK_PYTHON"] = sys.executable

spark = (SparkSession.builder.master("local[2]").appName("ch06")
         .config("spark.ui.enabled", "false").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

# 1. Данные: uid, uname, usage (минуты). Генерируем с фиксированным seed
r = random.Random(42)
data = [(i, f"user-{i:04d}", r.randrange(1000)) for i in range(1000)]
ds_usage = spark.createDataFrame(data, "uid INT, uname STRING, usage INT")

# 2. filter + orderBy: аналог filter(d => d.usage > 900) из книги
print("== usage > 900, top 3")
ds_usage.filter(col("usage") > 900).orderBy(desc("usage"), "uid").show(3)

# 3. Аналог map() с UsageCost: считаем cost и сохраняем остальные колонки
print("== cost per user")
cost = when(col("usage") > 750, col("usage") * 0.15).otherwise(col("usage") * 0.50)
ds_usage.withColumn("cost", cost).orderBy("uid").show(3)

# 4. Цена непрозрачной функции. Пишем данные в Parquet, читаем обратно
path = "/tmp/ch06_usage"
ds_usage.write.mode("overwrite").parquet(path)
df = spark.read.parquet(path)

@udf(BooleanType())
def over_900(u):  # Catalyst не видит, что внутри
    return u > 900

def plan(frame):
    """Показываем только нужное: фильтр, вызов Python и PushedFilters."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        frame.explain()
    out = []
    for line in buf.getvalue().splitlines():
        if "BatchEvalPython" in line or "ArrowEvalPython" in line:
            out.append("вызов Python UDF: да")
        m = re.search(r"PushedFilters: \[[^\]]*\]", line)
        if m:
            out.append(m.group(0))
    return "\n".join(out)

dsl = df.filter(col("usage") > 900)
fun = df.filter(over_900(col("usage")))
print("== plan: DSL")
print(plan(dsl))
print("== plan: UDF")
print(plan(fun))
print("== same result:", dsl.count(), fun.count())
spark.stop()
