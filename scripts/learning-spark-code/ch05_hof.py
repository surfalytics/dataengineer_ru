"""Глава 5: сложные типы: explode+collect_list, transform/filter/exists/reduce, встроенные функции массивов."""
import os, sys
from pyspark.sql import SparkSession

os.environ["PYSPARK_PYTHON"] = sys.executable

spark = (SparkSession.builder.master("local[2]").appName("Ch05Hof")
         .config("spark.ui.enabled", "false")
         .config("spark.sql.mapKeyDedupPolicy", "LAST_WIN")
         .config("spark.sql.warehouse.dir", "/tmp/ch05-warehouse").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

schema = "id int, celsius array<int>"
data = [(1, [35, 36, 32, 30, 40, 42, 38]), (2, [31, 32, 34, 55, 56])]
spark.createDataFrame(data, schema).createOrReplaceTempView("tC")

print("--- Вариант 1: explode + collect_list (нужен shuffle, порядок не гарантирован)")
spark.sql("""
    SELECT id, array_sort(collect_list(t + 1)) AS plus_one
    FROM (SELECT id, EXPLODE(celsius) AS t FROM tC) x
    GROUP BY id ORDER BY id
""").show(truncate=False)

print("--- transform")
spark.sql("""
    SELECT id, transform(celsius, t -> ((t * 9) div 5) + 32) AS fahrenheit
    FROM tC ORDER BY id
""").show(truncate=False)

print("--- filter")
spark.sql("SELECT id, filter(celsius, t -> t > 38) AS high FROM tC ORDER BY id").show(truncate=False)

print("--- exists")
spark.sql("SELECT id, exists(celsius, t -> t = 38) AS has_38 FROM tC ORDER BY id").show()

print("--- reduce")
spark.sql("""
    SELECT id, reduce(celsius, 0, (acc, t) -> acc + t,
                      acc -> (acc div size(celsius) * 9 div 5) + 32) AS avg_fahrenheit
    FROM tC ORDER BY id
""").show()

print("--- все четыре функции в одном запросе")
spark.sql("""
    SELECT id,
           transform(celsius, t -> ((t * 9) div 5) + 32) AS fahrenheit,
           filter(celsius, t -> t > 38) AS high,
           exists(celsius, t -> t = 38) AS has_38,
           reduce(celsius, 0, (acc, t) -> acc + t,
                  acc -> (acc div size(celsius) * 9 div 5) + 32) AS avg_fahrenheit
    FROM tC ORDER BY id
""").show(truncate=False)

print("--- встроенные функции массивов")
spark.sql("""
    SELECT array_distinct(array(1, 2, 3, null, 3)) AS dist,
           array_intersect(array(1, 2, 3), array(1, 3, 5)) AS inter,
           array_union(array(1, 2, 3), array(1, 3, 5)) AS uni,
           array_except(array(1, 2, 3), array(1, 3, 5)) AS exc,
           arrays_overlap(array(1, 2, 3), array(3, 4, 5)) AS overlap,
           flatten(array(array(1, 2), array(3, 4))) AS flat
""").show(truncate=False)
spark.sql("""
    SELECT map_concat(map(1, 'a', 2, 'b'), map(2, 'c', 3, 'd')) AS merged,
           element_at(map(1, 'a', 2, 'b'), 2) AS val
""").show(truncate=False)

spark.stop()
