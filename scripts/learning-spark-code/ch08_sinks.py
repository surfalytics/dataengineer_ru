"""Глава 8: file sink, foreachBatch (несколько sink, дедупликация по batchId), foreach, listener."""
import json, os, pathlib, shutil, sys, time
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.streaming import StreamingQueryListener
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

os.environ["PYSPARK_PYTHON"] = sys.executable
spark = (SparkSession.builder.master("local[2]").appName("ch08-sinks")
         .config("spark.ui.enabled", "false")
         .config("spark.sql.shuffle.partitions", 2).getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

base = pathlib.Path("/tmp/ch08_sinks")
shutil.rmtree(base, ignore_errors=True)
src = base / "in"
src.mkdir(parents=True)
for i in range(3):   # три файла = три micro-batch
    f = src / f"b{i}.json"
    f.write_text("".join(json.dumps({"key": i * 10 + j, "value": j}) + "\n" for j in range(2)))
    os.utime(f, (1_000_000 + i, 1_000_000 + i))

schema = StructType([StructField("key", IntegerType()), StructField("value", IntegerType())])
def source():
    return spark.readStream.schema(schema).option("maxFilesPerTrigger", 1).json(str(src))

# Листенер: события start / progress / terminated (в PySpark он есть с версии 3.4)
events = []
class MyListener(StreamingQueryListener):
    def onQueryStarted(self, event): events.append("started")
    def onQueryProgress(self, event): events.append(f"progress rows={event.progress.numInputRows}")
    def onQueryIdle(self, event): pass
    def onQueryTerminated(self, event): events.append("terminated")
spark.streams.addListener(MyListener())

# 1. file sink: только append, журнал _spark_metadata
out = base / "parquet"
(source().writeStream.format("parquet").option("path", str(out))
    .option("checkpointLocation", str(base / "ck1")).trigger(availableNow=True).start().awaitTermination())
print("file sink:", spark.read.parquet(str(out)).count(), "строк,",
      "журнал есть:", (out / "_spark_metadata").is_dir())

# 2. foreachBatch: persist, запись в две папки, дедупликация по batchId
done = set()
def write_two(batch_df, batch_id):
    if batch_id in done:                    # повторный запуск micro-batch не пишем второй раз
        return
    batch_df.persist()                      # чтобы не считать batch два раза
    batch_df.write.mode("append").parquet(str(base / "loc1"))
    batch_df.write.mode("append").parquet(str(base / "loc2"))
    batch_df.unpersist()
    done.add(batch_id)
(source().writeStream.foreachBatch(write_two).option("checkpointLocation", str(base / "ck2"))
    .trigger(availableNow=True).start().awaitTermination())
print("foreachBatch:", spark.read.parquet(str(base / "loc1")).count(),
      spark.read.parquet(str(base / "loc2")).count(), "строк в двух местах")

# 3. foreach: свой writer с open / process / close (на каждую partition)
class LineWriter:
    def open(self, partition_id, epoch_id):
        self.f = open(base / f"foreach_{partition_id}_{epoch_id}.txt", "w")
        return True
    def process(self, row):
        self.f.write(f"{row.key}\n")
    def close(self, error):
        self.f.close()
(source().writeStream.foreach(LineWriter()).option("checkpointLocation", str(base / "ck3"))
    .trigger(availableNow=True).start().awaitTermination())
keys = sorted(int(x) for p in base.glob("foreach_*.txt") for x in p.read_text().split())
print("foreach:", keys)

time.sleep(2)   # листенер получает события асинхронно
print("listener:", events[:3], "...", events[-1], "| всего событий:", len(events) > 5)
spark.stop()
