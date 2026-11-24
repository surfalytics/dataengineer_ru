"""Глава 1: SparkSession, temporary view и SQL-запрос по DataFrame."""
import os, sys
from pyspark.sql import SparkSession

# worker использует тот же Python, что и driver
os.environ["PYSPARK_PYTHON"] = sys.executable

spark = (SparkSession.builder.master("local[2]").appName("LearnSpark")
         .config("spark.sql.shuffle.partitions", 6)
         .config("spark.ui.enabled", "false").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

# Маленькая таблица «коммитеров» вместо JSON на S3
rows = [
    ("Ana", "databricks", "mllib", 14),
    ("Boris", "apple", "mllib", 9),
    ("Chen", "databricks", "sql", 120),
    ("Dina", "google", "mllib", 31),
    ("Egor", "ibm", "mllib", 11),
    ("Farid", "google", "streaming", 50),
]
committers = spark.createDataFrame(rows, ["name", "org", "module", "num_commits"])

# DataFrame превращаем в temporary view: теперь к нему можно писать SQL
committers.createOrReplaceTempView("committers")

results = spark.sql("""
    SELECT name, org, module, num_commits
    FROM committers
    WHERE module = 'mllib' AND num_commits > 10
    ORDER BY num_commits DESC
""")
results.show()

# Тот же запрос через DataFrame API: план и результат одинаковые
same = (committers.filter("module = 'mllib' AND num_commits > 10")
        .orderBy(committers.num_commits.desc()).select("name", "org", "module", "num_commits"))
print("same result:", same.collect() == results.collect())
print("shuffle.partitions =", spark.conf.get("spark.sql.shuffle.partitions"))
spark.stop()
