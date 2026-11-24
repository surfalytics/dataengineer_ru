"""Глава 11: Spark без MLlib. mapInPandas (инференс), applyInPandas (модель на группу), pandas API on Spark."""
import os, shutil, sys
import numpy as np
import pandas as pd
import pyspark.pandas as ps
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from pyspark.sql import SparkSession

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["GIT_PYTHON_REFRESH"] = "quiet"
spark = (SparkSession.builder.master("local[2]").appName("ch11-udf")
         .config("spark.ui.enabled", "false").config("spark.sql.shuffle.partitions", "4")
         .config("spark.sql.execution.arrow.pyspark.enabled", "false").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

# 1. Модель scikit-learn обучена на одной машине и сохранена как папка MLflow
rng = np.random.default_rng(42)
X = pd.DataFrame({"bedrooms": rng.integers(1, 5, 200).astype(float),
                  "accommodates": rng.integers(1, 9, 200).astype(float)})
y = 50 + 40 * X["bedrooms"] + 10 * X["accommodates"] + rng.normal(0, 5, 200)
sk = RandomForestRegressor(n_estimators=50, random_state=42).fit(X, y)
path = "/tmp/ch11-sk-model"
shutil.rmtree(path, ignore_errors=True)
mlflow.sklearn.save_model(sk, path, serialization_format="cloudpickle")

df = spark.createDataFrame(X.head(6).assign(id=range(6))).select("id", "bedrooms", "accommodates")

def predict(iterator):
    model = mlflow.sklearn.load_model(path)      # модель грузим один раз на весь iterator
    for features in iterator:
        out = pd.DataFrame({"id": features["id"]})
        out["prediction"] = model.predict(features[["bedrooms", "accommodates"]])
        yield out

df.mapInPandas(predict, "id long, prediction double") \
  .selectExpr("id", "round(prediction, 1) as prediction").orderBy("id").show()

# 2. Своя модель на каждую группу: applyInPandas. Здесь группа = тип устройства
dev = pd.DataFrame({"device_id": ["a"] * 50 + ["b"] * 50,
                    "t": list(range(50)) * 2})
dev["wear"] = np.where(dev["device_id"] == "a", 2.0, 0.5) * dev["t"] + rng.normal(0, 1, 100)

def build_model(pdf):
    lr = LinearRegression().fit(pdf[["t"]], pdf["wear"])
    return pd.DataFrame({"device_id": [pdf["device_id"].iloc[0]],
                         "slope": [float(lr.coef_[0])], "n": [len(pdf)]})

spark.createDataFrame(dev).groupBy("device_id") \
    .applyInPandas(build_model, schema="device_id string, slope double, n long") \
    .selectExpr("device_id", "round(slope, 2) as slope", "n").orderBy("device_id").show()

# 3. Бывший Koalas: теперь pyspark.pandas, API как у pandas
kdf = ps.DataFrame({"duration": [10, 20, 30]})
kdf["duration_new"] = kdf["duration"] + 100
print(kdf.sort_index().to_pandas())
print(type(kdf.to_spark()).__name__)  # назад в обычный Spark DataFrame
spark.stop()
