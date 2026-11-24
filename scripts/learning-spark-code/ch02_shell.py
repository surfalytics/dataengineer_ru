from pyspark.sql import SparkSession

spark = (SparkSession.builder.master("local[2]").appName("Ch02Shell")
         .config("spark.ui.enabled", "false").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

# Готовим небольшой текстовый файл: 12 строк, в 5 из них есть слово Spark
lines = []
for i in range(12):
    lines.append(f"Spark line {i}" if i % 2 == 0 and i < 10 else f"plain line {i}")
with open("/tmp/readme.txt", "w") as f:
    f.write("\n".join(lines) + "\n")

print(spark.version)
strings = spark.read.text("/tmp/readme.txt")          # transformation
strings.orderBy("value").show(4, truncate=False)      # action
print(strings.count())                                # action

# filter() ничего не считает, count() запускает всё
filtered = strings.filter(strings.value.contains("Spark"))
print(filtered.count())
spark.stop()
