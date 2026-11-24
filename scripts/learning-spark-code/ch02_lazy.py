from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.types import BooleanType

spark = (SparkSession.builder.master("local[2]").appName("Ch02Lazy")
         .config("spark.ui.enabled", "false").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

# 1. Ленивое вычисление: накопитель считает, сколько раз вызвали нашу функцию
calls = spark.sparkContext.accumulator(0)

def is_even(x):
    calls.add(1)
    return x % 2 == 0

is_even_udf = udf(is_even, BooleanType())

df = spark.range(1000)                                # 1000 строк
filtered = df.filter(is_even_udf(col("id")))          # transformation
print("после filter:", calls.value)
print("строк в результате:", filtered.count())        # action
print("после count:", calls.value)

# 2. Narrow и wide: ищем Exchange (shuffle) в плане
narrow = df.filter("id % 2 = 0")
wide = df.groupBy((col("id") % 3).alias("k")).count()
print("--- filter (narrow)")
narrow.explain()
print("--- groupBy (wide)")
wide.explain()
spark.stop()
