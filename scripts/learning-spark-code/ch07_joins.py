"""Глава 7: broadcast hash join, sort merge join и bucketing."""
import io, os, re, shutil, sys
from contextlib import redirect_stdout
from pyspark.sql import SparkSession
from pyspark.sql.functions import broadcast, col, expr

os.environ["PYSPARK_PYTHON"] = sys.executable
WH = "/tmp/ch07_warehouse"          # внутри контейнера, не в репозитории
shutil.rmtree(WH, ignore_errors=True)

spark = (SparkSession.builder.master("local[2]").appName("joins")
         .config("spark.ui.enabled", "false")
         .config("spark.sql.warehouse.dir", WH)
         .config("spark.sql.shuffle.partitions", 4)
         .config("spark.sql.adaptive.enabled", "false")   # чтобы план не менялся во время работы
         .getOrCreate())
spark.sparkContext.setLogLevel("ERROR")


def plan(df):
    """Физический план без номеров (#12), только имена операторов."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        df.explain()
    ops = []
    for line in buf.getvalue().splitlines():
        m = re.search(r"(Exchange|Sort|SortMergeJoin|BroadcastHashJoin|BroadcastExchange|FileScan|Scan)\b", line)
        if m and "Physical Plan" not in line:
            ops.append(m.group(1))
    return " > ".join(ops)


# Данные: много заказов и маленький справочник пользователей
users = spark.range(10_000).select(col("id").alias("uid"), expr("concat('user_', id)").alias("login"))
orders = spark.range(100_000).select(
    col("id").alias("order_id"),
    (col("id") % 10_000).alias("users_id"),
    (col("id") % 7 * 10).alias("amount"))
small_users = users.where("uid < 100")

# 1. Маленькая таблица (меньше 10 МБ): Spark сам выбирает broadcast join
j1 = orders.join(small_users, orders.users_id == small_users.uid)
print("авто :", plan(j1))

# 2. Тот же join с подсказкой broadcast()
j2 = orders.join(broadcast(users), orders.users_id == users.uid)
print("hint :", plan(j2))

# 3. Порог -1 выключает broadcast: остаётся sort merge join
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
j3 = orders.join(users, orders.users_id == users.uid)
print("SMJ  :", plan(j3))
print("строк в join:", j3.count())

# 4. Bucketing: сохраняем обе таблицы по ключу с 8 бакетами
users.write.bucketBy(8, "uid").sortBy("uid").mode("overwrite").saveAsTable("users_b")
orders.write.bucketBy(8, "users_id").sortBy("users_id").mode("overwrite").saveAsTable("orders_b")
j4 = spark.table("orders_b").join(spark.table("users_b"), col("users_id") == col("uid"))
print("bucket:", plan(j4))
print("строк в join:", j4.count())

spark.stop()
shutil.rmtree(WH, ignore_errors=True)
