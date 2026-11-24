"""Глава 10: decision tree, maxBins, random forest, CrossValidator, parallelism, cv внутри Pipeline."""
import random
import time
from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml.regression import DecisionTreeRegressor, RandomForestRegressor
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator

spark = (SparkSession.builder.master("local[2]").appName("ch10-trees")
         .config("spark.ui.enabled", "false")
         .config("spark.sql.shuffle.partitions", "4").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

# Учебные данные. В колонке hood 36 разных районов: это больше, чем maxBins=32 по умолчанию
random.seed(7)
hood_names = [f"hood{i:02d}" for i in range(36)]
hood_eff = {h: random.uniform(-30, 60) for h in hood_names}
rooms = {"Entire home": 90.0, "Private room": 0.0, "Shared room": -30.0}
rows = []
for i in range(600):
    bed = float(random.choice([1, 1, 1, 2, 2, 3]))
    room = random.choice(list(rooms))
    hood = random.choice(hood_names)
    price = 50 + 70 * bed + rooms[room] + hood_eff[hood] + random.gauss(0, 25)
    rows.append((i, hood, room, bed, float(random.randint(0, 200)), round(max(price, 20.0), 1)))
df = spark.createDataFrame(
    rows, "id int, hood string, room_type string, bedrooms double, reviews double, price double")
train, test = df.randomSplit([.8, .2], seed=42)

cat_cols = ["hood", "room_type"]
idx_cols = [c + "Index" for c in cat_cols]
indexer = StringIndexer(inputCols=cat_cols, outputCols=idx_cols, handleInvalid="skip")
num_cols = ["bedrooms", "reviews"]
va = VectorAssembler(inputCols=idx_cols + num_cols, outputCol="features")

# 1. Decision tree с maxBins по умолчанию: ошибка
dt = DecisionTreeRegressor(labelCol="price")
try:
    Pipeline(stages=[indexer, va, dt]).fit(train)
except Exception as e:
    msg = str(e).split("\n")[0]
    print("ОШИБКА:", msg.split(". Consider")[0])

# 2. Увеличиваем maxBins до 40
dt.setMaxBins(40)
pm = Pipeline(stages=[indexer, va, dt]).fit(train)
dt_model = pm.stages[-1]
print("depth =", dt_model.depth, ", numNodes =", dt_model.numNodes)
imp = sorted(zip(va.getInputCols(), dt_model.featureImportances), key=lambda t: -t[1])
for name, value in imp:
    print(f"{name:12s} {value:.3f}")
ev = RegressionEvaluator(labelCol="price", predictionCol="prediction", metricName="rmse")
print(f"decision tree RMSE = {ev.evaluate(pm.transform(test)):.1f}")

# 3. Random forest + сетка гиперпараметров + 3-fold cross-validation
rf = RandomForestRegressor(labelCol="price", maxBins=40, seed=42)
grid = (ParamGridBuilder()
        .addGrid(rf.maxDepth, [2, 4, 6])
        .addGrid(rf.numTrees, [10, 50])
        .build())
cv = CrossValidator(estimator=Pipeline(stages=[indexer, va, rf]), evaluator=ev,
                    estimatorParamMaps=grid, numFolds=3, seed=42)
t0 = time.time()
cv_model = cv.fit(train)
t_seq = time.time() - t0
print("конфигураций:", len(grid), ", моделей: 3 x", len(grid), "+ 1 финальная =", 3 * len(grid) + 1)
for pm_, metric in zip(cv_model.getEstimatorParamMaps(), cv_model.avgMetrics):
    d = {p.name: v for p, v in pm_.items()}
    print(f"maxDepth={d['maxDepth']} numTrees={d['numTrees']:>2}  avg RMSE={metric:.1f}")
best = cv_model.bestModel.stages[-1]
print("лучшая модель: maxDepth =", best.getMaxDepth(), ", numTrees =", best.getNumTrees)
print(f"forest RMSE на test = {ev.evaluate(cv_model.transform(test)):.1f}")

# 4. parallelism=2
t0 = time.time()
cv2 = cv.setParallelism(2).fit(train)
t_par = time.time() - t0
print("те же метрики с parallelism=2:", [round(m, 1) for m in cv2.avgMetrics] == [round(m, 1) for m in cv_model.avgMetrics])

# 5. cv внутри Pipeline: StringIndexer учится один раз
cv_in = CrossValidator(estimator=rf, evaluator=ev, estimatorParamMaps=grid,
                       numFolds=3, parallelism=2, seed=42)
t0 = time.time()
pm2 = Pipeline(stages=[indexer, va, cv_in]).fit(train)
t_in = time.time() - t0
print(f"forest RMSE (cv внутри pipeline) = {ev.evaluate(pm2.transform(test)):.1f}")
# Время только в stderr: оно меняется от запуска к запуску
import sys
print(f"[время] sequential={t_seq:.1f}s parallel={t_par:.1f}s cv-inside={t_in:.1f}s", file=sys.stderr)
spark.stop()
