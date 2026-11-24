"""Глава 1: Structured Streaming. Поток как растущая таблица, word count."""
import tempfile, pathlib
import os, sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split

# worker использует тот же Python, что и driver
os.environ["PYSPARK_PYTHON"] = sys.executable

spark = (SparkSession.builder.master("local[2]").appName("streaming")
         .config("spark.ui.enabled", "false")
         .config("spark.sql.shuffle.partitions", 2).getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

# Вместо socket кладём файлы в папку: так поток можно воспроизвести
src = pathlib.Path(tempfile.mkdtemp())
(src / "a.txt").write_text("spark is fast\nspark is unified\n")
(src / "b.txt").write_text("hadoop is slow\n")

lines = spark.readStream.format("text").load(str(src))
words = lines.select(explode(split(lines.value, " ")).alias("word"))
word_counts = words.groupBy("word").count()

query = (word_counts.writeStream.format("memory").queryName("wc")
         .outputMode("complete").trigger(availableNow=True).start())
query.awaitTermination()
spark.sql("SELECT word, count FROM wc ORDER BY count DESC, word").show()
spark.stop()
