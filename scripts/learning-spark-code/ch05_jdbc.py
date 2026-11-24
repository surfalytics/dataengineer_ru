"""Глава 5: JDBC-источник и параллельное чтение (numPartitions, bounds).
Вместо PostgreSQL используем встроенную в Spark базу Derby в памяти: сервер и пароли не нужны."""
import os, sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import spark_partition_id

os.environ["PYSPARK_PYTHON"] = sys.executable

spark = (SparkSession.builder.master("local[2]").appName("Ch05Jdbc")
         .config("spark.ui.enabled", "false")
         .config("spark.sql.warehouse.dir", "/tmp/ch05-warehouse").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

URL = "jdbc:derby:memory:orders;create=true"
DRIVER = "org.apache.derby.jdbc.EmbeddedDriver"

# Derby хранит имена в верхнем регистре, поэтому пишем их так же
# 1. Пишем 2000 заказов в «внешнюю» базу. id идут от 2000 до 3999
orders = spark.range(2000, 4000).selectExpr("id AS ORDER_ID", "id % 7 AS SHOP_ID")
(orders.write.format("jdbc").option("url", URL).option("driver", DRIVER)
    .option("dbtable", "ORDERS").mode("overwrite").save())

# 2. Чтение без партиций: один запрос, одна partition
single = (spark.read.format("jdbc").option("url", URL).option("driver", DRIVER)
          .option("dbtable", "ORDERS").load())
print("без partitionColumn: partition =", single.rdd.getNumPartitions(), ", строк =", single.count())

def read(lower, upper, n):
    return (spark.read.format("jdbc").option("url", URL).option("driver", DRIVER)
            .option("dbtable", "ORDERS").option("partitionColumn", "ORDER_ID")
            .option("lowerBound", lower).option("upperBound", upper)
            .option("numPartitions", n).load())

def sizes(df):
    rows = df.groupBy(spark_partition_id().alias("p")).count().orderBy("p").collect()
    return [r["count"] for r in rows]

def report(label, df):
    print(label, sizes(df), "всего строк:", df.count())

# 3. Границы равны реальным значениям: нагрузка ровная
report("bounds 2000..4000, 10 partitions:", read(2000, 4000, 10))

# 4. Границы 1000..10000, а данные только в 2000..3999: работают 3 partition из 10
report("bounds 1000..10000, 10 partitions:", read(1000, 10000, 10))

# 5. Границы не фильтруют строки: они только задают шаг (stride)
report("bounds 3000..3500, 2 partitions:", read(3000, 3500, 2))

# 6. query вместо dbtable: фильтр выполняет сама база
q = (spark.read.format("jdbc").option("url", URL).option("driver", DRIVER)
     .option("query", "SELECT SHOP_ID, COUNT(*) AS CNT FROM ORDERS GROUP BY SHOP_ID")
     .load().orderBy("SHOP_ID"))
q.show()

spark.stop()
