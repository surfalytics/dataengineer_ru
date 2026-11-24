"""Глава 7: читаем и меняем конфигурацию Spark из кода."""
import os, sys
from pyspark.sql import SparkSession

os.environ["PYSPARK_PYTHON"] = sys.executable

# Значения из builder — самый «сильный» уровень (выше spark-defaults.conf и --conf)
spark = (SparkSession.builder.master("local[2]").appName("config")
         .config("spark.ui.enabled", "false")
         .config("spark.sql.shuffle.partitions", 5)
         .config("spark.executor.memory", "2g")
         .getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

# Читаем конфигурацию
print("master:", spark.conf.get("spark.master"))
print("executor.memory:", spark.conf.get("spark.executor.memory"))
print("shuffle.partitions:", spark.conf.get("spark.sql.shuffle.partitions"))

# Какие настройки можно менять во время работы
for key in ["spark.sql.shuffle.partitions", "spark.executor.memory"]:
    print("isModifiable", key, "->", spark.conf.isModifiable(key))

# Меняем настройку через API
spark.conf.set("spark.sql.shuffle.partitions", 3)
print("после set:", spark.conf.get("spark.sql.shuffle.partitions"))

# Настройки, которые мы не задавали: значения по умолчанию
print("autoBroadcastJoinThreshold:", spark.conf.get("spark.sql.autoBroadcastJoinThreshold"))
print("adaptive.enabled:", spark.conf.get("spark.sql.adaptive.enabled"))
print("files.maxPartitionBytes:", spark.conf.get("spark.sql.files.maxPartitionBytes"))
print("dynamicAllocation.enabled:", spark.conf.get("spark.dynamicAllocation.enabled", "false"))

# Только настройки Spark SQL: SET -v
spark.sql("SET -v").select("key", "value").where("key = 'spark.sql.shuffle.partitions'").show(truncate=False)
spark.stop()
