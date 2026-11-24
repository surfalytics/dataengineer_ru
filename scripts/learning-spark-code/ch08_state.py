"""Глава 8: произвольное состояние (applyInPandasWithState) с timeout по event time."""
import json, os, pathlib, shutil, sys
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import to_timestamp
from pyspark.sql.streaming.state import GroupStateTimeout
from pyspark.sql.types import StructType, StructField, StringType, LongType

os.environ["PYSPARK_PYTHON"] = sys.executable
spark = (SparkSession.builder.master("local[2]").appName("ch08-state")
         .config("spark.ui.enabled", "false")
         .config("spark.sql.session.timeZone", "UTC")
         .config("spark.sql.shuffle.partitions", 2).getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

base = pathlib.Path("/tmp/ch08_state")
shutil.rmtree(base, ignore_errors=True)
src = base / "in"
src.mkdir(parents=True)
batches = [
    [("u1", "login", "12:00"), ("u2", "login", "12:01")],
    [("u1", "click", "12:05")],
    [("u3", "login", "13:00")],
    [("u4", "login", "14:00")],
]
for i, rows in enumerate(batches):
    f = src / f"b{i}.json"
    f.write_text("".join(json.dumps({"userId": u, "action": a, "eventTime": f"2026-01-01 {t}:00"}) + "\n"
                         for u, a, t in rows))
    os.utime(f, (1_000_000 + i, 1_000_000 + i))

schema = StructType([StructField("userId", StringType()), StructField("action", StringType()),
                     StructField("eventTime", StringType())])
actions = (spark.readStream.schema(schema).option("maxFilesPerTrigger", 1).json(str(src))
           .withColumn("eventTime", to_timestamp("eventTime"))
           .withWatermark("eventTime", "10 minutes"))

out_schema = StructType([StructField("userId", StringType()), StructField("status", StringType()),
                         StructField("actions", LongType())])
state_schema = StructType([StructField("actions", LongType())])
ONE_HOUR_MS = 3600 * 1000

def update_status(key, pdf_iter, state):
    """Вызывается для ключа, у которого есть новые данные, или у которого сработал timeout."""
    user = key[0]
    if state.hasTimedOut:                       # данных нет, но пора убрать состояние
        (n,) = state.get
        state.remove()
        yield pd.DataFrame({"userId": [user], "status": ["inactive"], "actions": [n]})
        return
    n = state.get[0] if state.exists else 0     # прошлое состояние, если оно есть
    last = None
    for pdf in pdf_iter:                        # порядок строк не определён
        n += len(pdf)
        last = pdf["eventTime"].max() if last is None else max(last, pdf["eventTime"].max())
    state.update((n,))
    # timeout: максимальное event time ключа + 1 час (в миллисекундах)
    state.setTimeoutTimestamp(int(last.timestamp() * 1000) + ONE_HOUR_MS)
    yield pd.DataFrame({"userId": [user], "status": ["active"], "actions": [n]})

result = (actions.groupBy("userId")
          .applyInPandasWithState(update_status, out_schema, state_schema,
                                  "append", GroupStateTimeout.EventTimeTimeout))

def show(df, batch_id):
    rows = df.orderBy("userId").collect()
    print(f"batch {batch_id}:", "; ".join(f"{r.userId} {r.status} ({r.actions})" for r in rows) or "-")

(result.writeStream.foreachBatch(show).option("checkpointLocation", str(base / "ck"))
    .trigger(availableNow=True).start().awaitTermination())
spark.stop()
