"""Глава 11: MLflow. Tracking, загрузка модели, batch-прогноз, Model Registry."""
import os, shutil, sys
os.environ["GIT_PYTHON_REFRESH"] = "quiet"  # в контейнере нет git
import numpy as np
import pandas as pd
import mlflow, mlflow.spark
from mlflow.tracking import MlflowClient
from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml.evaluation import RegressionEvaluator

os.environ["PYSPARK_PYTHON"] = sys.executable
spark = (SparkSession.builder.master("local[2]").appName("ch11-mlflow")
         .config("spark.ui.enabled", "false").config("spark.sql.shuffle.partitions", "4")
         .config("spark.sql.execution.arrow.pyspark.enabled", "false")
         .getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

# Данные: 400 объявлений аренды, цена зависит от комнат, гостей и района
rng = np.random.default_rng(42)
n = 400
pdf = pd.DataFrame({
    "neighbourhood": rng.choice(["center", "beach", "hills"], n),
    "bedrooms": rng.integers(1, 5, n).astype(float),
    "accommodates": rng.integers(1, 9, n).astype(float),
})
base = {"center": 120.0, "beach": 150.0, "hills": 90.0}
pdf["price"] = (pdf["neighbourhood"].map(base) + 40 * pdf["bedrooms"]
                + 10 * pdf["accommodates"] + rng.normal(0, 20, n))
airbnb = spark.createDataFrame(pdf)
train, test = airbnb.randomSplit([.8, .2], seed=42)

# Pipeline: индекс района -> вектор признаков -> случайный лес
indexer = StringIndexer(inputCol="neighbourhood", outputCol="neighbourhoodIndex")
assembler = VectorAssembler(inputCols=["neighbourhoodIndex", "bedrooms", "accommodates"],
                            outputCol="features")
rf = RandomForestRegressor(labelCol="price", maxBins=40, maxDepth=5, numTrees=100, seed=42)
pipeline = Pipeline(stages=[indexer, assembler, rf])

# Локальное хранилище MLflow. Сервер не нужен
# В MLflow 3 файловое хранилище в режиме поддержки: берём SQLite, артефакты кладём в папку
shutil.rmtree("/tmp/ch11-mlflow", ignore_errors=True)
os.makedirs("/tmp/ch11-mlflow")
mlflow.set_tracking_uri("sqlite:////tmp/ch11-mlflow/mlflow.db")
exp_id = mlflow.create_experiment("airbnb-price", artifact_location="file:///tmp/ch11-mlflow/artifacts")
mlflow.set_experiment(experiment_id=exp_id)

with mlflow.start_run(run_name="random-forest") as run:
    mlflow.log_param("num_trees", rf.getNumTrees())
    mlflow.log_param("max_depth", rf.getMaxDepth())

    model = pipeline.fit(train)
    mlflow.spark.log_model(model, artifact_path="model")

    pred = model.transform(test)
    ev = RegressionEvaluator(predictionCol="prediction", labelCol="price")
    rmse = ev.setMetricName("rmse").evaluate(pred)
    r2 = ev.setMetricName("r2").evaluate(pred)
    mlflow.log_metrics({"rmse": rmse, "r2": r2})

    # Артефакт: важность признаков. Сначала файл на диск, потом в MLflow
    imp = (pd.DataFrame(list(zip(assembler.getInputCols(), model.stages[-1].featureImportances)),
                        columns=["feature", "importance"])
           .sort_values("importance", ascending=False))
    imp.to_csv("/tmp/feature-importance.csv", index=False)
    mlflow.log_artifact("/tmp/feature-importance.csv")

# Запрос к tracking: последний запуск и его метрики
client = MlflowClient()
runs = client.search_runs(run.info.experiment_id, order_by=["attributes.start_time desc"],
                          max_results=1)
print("run name:", runs[0].info.run_name)
print("params:", dict(sorted(runs[0].data.params.items())))
print("metrics:", {k: round(v, 2) for k, v in sorted(runs[0].data.metrics.items())})

# Batch: загружаем модель по URI запуска и применяем ко всему DataFrame
loaded = mlflow.spark.load_model(f"runs:/{run.info.run_id}/model")
loaded.transform(test).select("neighbourhood", "bedrooms", "accommodates", "price", "prediction") \
    .withColumnRenamed("prediction", "pred").orderBy("neighbourhood", "bedrooms", "accommodates", "price") \
    .limit(3).selectExpr("neighbourhood", "bedrooms", "accommodates", "round(price, 1) as price",
                         "round(pred, 1) as pred").show()

# Model Registry: версия и alias "production"
name = "airbnb-rf"
mv = mlflow.register_model(f"runs:/{run.info.run_id}/model", name)
client.set_registered_model_alias(name, "production", mv.version)
prod = mlflow.spark.load_model(f"models:/{name}@production")
print("registry version:", mv.version, "| rows scored:", prod.transform(test).count())
spark.stop()
