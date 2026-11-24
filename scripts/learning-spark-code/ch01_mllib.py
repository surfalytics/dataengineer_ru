"""Глава 1: MLlib. fit на training, transform на test."""
import os, sys
from pyspark.sql import SparkSession
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.linalg import Vectors

# worker использует тот же Python, что и driver
os.environ["PYSPARK_PYTHON"] = sys.executable

spark = (SparkSession.builder.master("local[2]").appName("mllib")
         .config("spark.ui.enabled", "false").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

# Две группы точек: label 0 около (0, 0), label 1 около (3, 3)
train_rows = [(0.0, Vectors.dense(0.1, 0.2)), (0.0, Vectors.dense(0.4, 0.1)),
              (0.0, Vectors.dense(0.3, 0.5)), (0.0, Vectors.dense(0.0, 0.4)),
              (1.0, Vectors.dense(2.9, 3.1)), (1.0, Vectors.dense(3.2, 2.8)),
              (1.0, Vectors.dense(3.5, 3.3)), (1.0, Vectors.dense(2.7, 3.0))]
test_rows = [(0.0, Vectors.dense(0.2, 0.3)), (1.0, Vectors.dense(3.0, 3.0))]
training = spark.createDataFrame(train_rows, ["label", "features"])
test = spark.createDataFrame(test_rows, ["label", "features"])

lr = LogisticRegression(maxIter=10, regParam=0.3, elasticNetParam=0.8)  # Estimator
lr_model = lr.fit(training)                                              # Transformer
lr_model.transform(test).select("label", "prediction").orderBy("label").show()
spark.stop()
