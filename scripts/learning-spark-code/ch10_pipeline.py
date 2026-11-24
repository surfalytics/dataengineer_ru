"""Глава 10: данные, train/test, Transformer, Estimator, Pipeline, OHE, RMSE, R2, save/load."""
import random
import shutil
from pyspark.sql import SparkSession
from pyspark.ml import Pipeline, PipelineModel
from pyspark.ml.feature import VectorAssembler, StringIndexer, OneHotEncoder
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.linalg import Vectors
from pyspark.sql import functions as F

spark = (SparkSession.builder.master("local[2]").appName("ch10")
         .config("spark.ui.enabled", "false")
         .config("spark.sql.shuffle.partitions", "4").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

# Учебные данные: аренда жилья. Цена зависит от спален, типа жилья и района
random.seed(42)
rooms = {"Entire home": 90.0, "Private room": 0.0, "Shared room": -30.0}
hoods = {"Mission": 40.0, "Marina": 60.0, "Sunset": 0.0, "Haight": 20.0}
rows = []
for i in range(400):
    bed = float(random.choice([1, 1, 1, 2, 2, 3]))
    room = random.choice(list(rooms))
    hood = random.choice(list(hoods))
    price = 50 + 70 * bed + rooms[room] + hoods[hood] + random.gauss(0, 25)
    rows.append((i, hood, room, bed, round(max(price, 20.0), 1)))
df = spark.createDataFrame(rows, "id int, hood string, room_type string, bedrooms double, price double")

# 1. train/test 80/20 с seed
train, test = df.randomSplit([.8, .2], seed=42)
print(f"train={train.count()}, test={test.count()}")

# 2. Transformer: VectorAssembler собирает признаки в один вектор
va1 = VectorAssembler(inputCols=["bedrooms"], outputCol="features")
va1.transform(train).select("bedrooms", "features", "price").orderBy("price", "bedrooms").show(3)

# 3. Estimator: LinearRegression.fit возвращает Model (это Transformer)
lr = LinearRegression(featuresCol="features", labelCol="price")
lr_model = lr.fit(va1.transform(train))
print(f"price = {lr_model.coefficients[0]:.2f}*bedrooms + {lr_model.intercept:.2f}")

# 4. Pipeline из двух стадий
pm = Pipeline(stages=[va1, lr]).fit(train)
pm.transform(test).select("bedrooms", "price", "prediction").orderBy("price", "bedrooms").show(3)

# 5. One-hot encoding: StringIndexer -> OneHotEncoder -> VectorAssembler
cat_cols = [f for f, t in train.dtypes if t == "string"]
idx_cols = [c + "Index" for c in cat_cols]
ohe_cols = [c + "OHE" for c in cat_cols]
indexer = StringIndexer(inputCols=cat_cols, outputCols=idx_cols, handleInvalid="skip")
ohe = OneHotEncoder(inputCols=idx_cols, outputCols=ohe_cols)
num_cols = [f for f, t in train.dtypes if t == "double" and f != "price"]
va = VectorAssembler(inputCols=ohe_cols + num_cols, outputCol="features")
lr = LinearRegression(labelCol="price", featuresCol="features")
pm = Pipeline(stages=[indexer, ohe, va, lr]).fit(train)
pred = pm.transform(test)
print(pred.orderBy("id").select("features").first()[0])

# 6. Метрики: RMSE, R2 и baseline (среднее по train)
ev = RegressionEvaluator(predictionCol="prediction", labelCol="price", metricName="rmse")
print(f"RMSE is {ev.evaluate(pred):.1f}")
print(f"R2 is {ev.setMetricName('r2').evaluate(pred):.3f}")
mean_price = train.agg(F.avg("price")).first()[0]
base = test.withColumn("prediction", F.lit(mean_price))
print(f"baseline RMSE is {ev.setMetricName('rmse').evaluate(base):.1f}")

# 7. Сохранить и загрузить Pipeline целиком
path = "/tmp/ch10-lr-pipeline"
shutil.rmtree(path, ignore_errors=True)
pm.write().overwrite().save(path)
loaded = PipelineModel.load(path)
same = loaded.transform(test).agg(F.sum("prediction")).first()[0] == pred.agg(F.sum("prediction")).first()[0]
print("после load предсказания те же:", same)
shutil.rmtree(path, ignore_errors=True)

# 8. SparseVector
print(Vectors.sparse(10, [3, 5], [7.0, 2.0]).toArray())
spark.stop()
