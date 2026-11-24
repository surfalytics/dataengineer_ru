"""Глава 8: поток как растущая таблица. Word count, режимы вывода, checkpoint, restart."""
import os, pathlib, shutil, sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, split
from pyspark.errors import AnalysisException

os.environ["PYSPARK_PYTHON"] = sys.executable
spark = (SparkSession.builder.master("local[2]").appName("ch08-wordcount")
         .config("spark.ui.enabled", "false")
         .config("spark.sql.shuffle.partitions", 2).getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

base = pathlib.Path("/tmp/ch08_wc")
shutil.rmtree(base, ignore_errors=True)
src = base / "in"
src.mkdir(parents=True)
(src / "a.txt").write_text("spark is fast\nspark is unified\n")
(src / "b.txt").write_text("hadoop is slow\n")

# Шаги 1-2: источник и преобразование. Код такой же, как для batch DataFrame.
lines = (spark.readStream.format("text")
         .option("maxFilesPerTrigger", 1).load(str(src)))   # один файл на micro-batch
words = lines.select(explode(split(col("value"), " ")).alias("word"))
counts = words.groupBy("word").count()

def show_batch(df, batch_id):
    rows = [f"{r.word}={r['count']}" for r in df.orderBy("word").collect()]
    print(f"batch {batch_id}:", " ".join(rows))

def run(mode, ckpt):
    # Шаги 3-5: sink, режим вывода, checkpoint, trigger, start
    q = (counts.writeStream.foreachBatch(show_batch).outputMode(mode)
         .option("checkpointLocation", str(base / ckpt))
         .trigger(availableNow=True).start())
    q.awaitTermination()
    return q

print("=== update: каждый micro-batch выводит только изменённые строки")
run("update", "ck_update")

print("=== complete: каждый micro-batch выводит всю таблицу")
q = run("complete", "ck_complete")
p = q.lastProgress
print("lastProgress:", p["batchId"], p["numInputRows"], p["sources"][0]["description"][:20])

print("=== append для агрегации без watermark не поддерживается")
try:
    counts.writeStream.foreachBatch(show_batch).outputMode("append").start()
except AnalysisException as e:
    print(e.getCondition())

print("=== restart с тем же checkpoint: новый файл, старые счётчики из state")
(src / "c.txt").write_text("spark is great\n")
run("complete", "ck_complete")
spark.stop()
