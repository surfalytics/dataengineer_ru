---
title: "Learning Spark, глава 11: MLflow, развёртывание и масштабирование моделей"
head:
  - tag: title
    content: "MLflow и развёртывание ML-моделей в Spark | Инжиниринг Данных"
description: "Конспект главы 11 Learning Spark на русском. MLflow Tracking и Registry, batch, streaming и real-time, pandas UDF, Hyperopt, Koalas."
sidebar:
  order: 11
  label: "11. MLflow, развёртывание и масштабирование моделей"
tags:
  - books
  - spark
  - mlflow
---

**Главная мысль:** обученная модель ещё не готова к работе. Сначала её нужно уметь воспроизвести и отследить, потом выбрать способ запуска: `batch`, `streaming` или `real-time`. С воспроизводимостью помогает MLflow, а режим выбирают по требованиям к задержке.

## О чём глава

В [главе 10](/book-summaries/engineering/learning-spark/10-mllib/) мы строили `ML pipeline` в MLlib. Теперь вопрос другой: как вести такие модели и запускать их в работу. Темы: воспроизводимость и MLflow, режимы `batch`, `streaming` и `real-time`, Spark без MLlib (pandas UDF, подбор гиперпараметров, Koalas).

![Схема: MLflow ведёт модель от запуска обучения через Tracking, Models и Registry к развёртыванию](/assets/learning-spark/ch11-mlflow-components.png)

Слева направо идёт путь модели: от запуска обучения до выдачи версии в работу.

## Управление моделями

Модель нужно уметь воспроизвести. Это шире, чем «зафиксировать seed»: нужно повторить код, окружение, данные и саму модель. Мешают четыре вещи:

- **Версии библиотек.** Новая версия может иначе вести себя по умолчанию: XGBoost в версии 0.90 изменил обработку пропусков.
- **Изменение данных.** Модель от 1 июня нельзя повторить 1 июля, если в данные добавили колонку или в десять раз больше строк.
- **Порядок выполнения.** Ноутбук запускают не сверху вниз или повторяют ячейку с состоянием. Иногда в репозиторий попадает код с другими гиперпараметрами.
- **Параллельные операции.** GPU считает параллельно, и порядок не гарантирован. Сумма чисел с плавающей точкой зависит от порядка слагаемых, и результат слегка меняется.

Если эксперимент не воспроизвести, бизнес часто не принимает модель. Собственные инструменты для учёта моделей, данных и версий быстро устаревают и требуют много сил на поддержку, а общий стандарт нужен, чтобы передавать модели партнёрам. Авторы берут MLflow: у него самая тесная интеграция с MLlib среди open source инструментов.

## MLflow

MLflow — это open source платформа для воспроизведения экспериментов и управления моделями. Интерфейсы: Python, R, Java, Scala и REST API. Установка: `pip install mlflow`. У неё четыре компонента (схема выше). Первый, `Tracking`, записывает параметры, метрики и версии кода. Второй, `Projects`, упаковывает проект с зависимостями для запуска на другой платформе. Компонент `Models` задаёт единый формат модели и общий API загрузки для любой библиотеки. А `Registry` хранит версии, статусы и пометки.

### Tracking

`Tracking` — это API логирования, не зависящий от библиотеки и окружения. Он строится вокруг `run` (один запуск кода обучения). Запуски собираются в `experiment`. Логировать можно из ноутбука, приложения или облачного job. На сервер попадает:

- **Parameters:** входы кода, например `num_trees`.
- **Metrics:** числа, которые могут обновляться, например RMSE.
- **Artifacts:** файлы и данные, например картинки и Parquet.
- **Metadata:** источник запуска и версия кода, скажем хеш Git-коммита.
- **Models:** сами обученные модели.

По умолчанию сервер пишет всё в файловую систему, а для быстрых запросов подключают базу данных. Сокращённый код главы на наших данных (`random forest` предсказывает цену аренды):

```python
with mlflow.start_run(run_name="random-forest") as run:
    mlflow.log_param("num_trees", rf.getNumTrees())
    mlflow.log_param("max_depth", rf.getMaxDepth())

    model = pipeline.fit(train)
    mlflow.spark.log_model(model, artifact_path="model")

    pred = model.transform(test)
    rmse = ev.setMetricName("rmse").evaluate(pred)
    r2 = ev.setMetricName("r2").evaluate(pred)
    mlflow.log_metrics({"rmse": rmse, "r2": r2})
    mlflow.log_artifact("/tmp/feature-importance.csv")   # CSV с важностью признаков

# Запрос к tracking: последний запуск
runs = MlflowClient().search_runs(run.info.experiment_id,
        order_by=["attributes.start_time desc"], max_results=1)
print(runs[0].data.metrics)
```

```text
params: {'max_depth': '5', 'num_trees': '100'}
metrics: {'r2': 0.77, 'rmse': 30.44}
```

У нас данные синтетические (в книге на Airbnb вышло `r2` около 0,23). Полный скрипт: [ch11_mlflow.py](https://github.com/surfalytics/dataengineer_ru/blob/main/scripts/learning-spark-code/ch11_mlflow.py). Запуск описан в [главе 1](/book-summaries/engineering/learning-spark/01-intro-to-spark/).

> **Пояснение:** в MLflow 3.18 файловое хранилище отключено по умолчанию, поэтому скрипт использует SQLite. Сервер не нужен.

В интерфейсе (команда `mlflow ui`, здесь не запускалась) запуски ищут, сравнивают рядом и выгружают в CSV. Заметки и теги к запуску добавлять можно, а параметры и метрики после его окончания менять нельзя.

Код книги выложен как MLflow project: YAML-файл описывает зависимости, и запуск повторяется где угодно.

```python
# не запускается: нужен репозиторий книги в GitHub
mlflow.run("https://github.com/databricks/LearningSparkV2/#mlflow-project-example",
           parameters={"max_depth": 5, "num_trees": 100})
```

## Варианты развёртывания моделей MLlib

Что значит «развернуть модель», зависит от организации. Требования к задержке, пропускной способности и стоимости определяют режим: `batch`, `streaming`, `real-time` или мобильное устройство (его авторы не разбирают).

| Режим | Пропускная способность | Задержка | Пример |
|---|---|---|---|
| `batch` | высокая | часы или дни | прогноз оттока клиентов |
| `streaming` | средняя | секунды или минуты | динамическая цена |
| `real-time` | низкая | миллисекунды | ставки в онлайн-рекламе |

![Схема: режимы batch, streaming, near real-time и real-time, и где MLlib подходит](/assets/learning-spark/ch11-deploy-options.png)

Чем левее режим, тем выше задержка и пропускная способность.

Требования к развёртыванию нужно определить до начала моделирования.

### Batch

Это самый частый и простой способ: регулярный job считает прогнозы и пишет их в таблицу, базу или `data lake`. Он и самый дешёвый: платим только за время запуска, а накладные расходы делятся на все прогнозы. В Spark это важно: обмен между `driver` и `executor` дорог, поэтому считать прогнозы по одной записи невыгодно. Минус: задержка в часы и дни.

`model.transform()` применяет модель параллельно ко всем `partition`:

```python
loaded = mlflow.spark.load_model(f"runs:/{run.info.run_id}/model")
loaded.transform(test)   # прогноз для всех строк
```

```text
+-------------+--------+------------+-----+-----+
|neighbourhood|bedrooms|accommodates|price| pred|
+-------------+--------+------------+-----+-----+
|        beach|     1.0|         1.0|188.4|233.4|
|        beach|     1.0|         2.0|171.3|232.0|
|        beach|     1.0|         2.0|230.0|232.0|
+-------------+--------+------------+-----+-----+
```

У `batch` три вопроса:

- **Как часто считать прогнозы?** Чем больше пачка, тем выше пропускная способность, но дольше ждать каждый прогноз.
- **Как часто переобучать?** В отличие от `sklearn` и TensorFlow, MLlib не умеет онлайн-обновление и `warm start`: модель переобучают целиком. Одни делают это по расписанию (раз в месяц), другие следят за `model drift` (качество падает, потому что данные изменились) и переобучают по сигналу.
- **Как версионировать?** Для этого служит Model Registry со статусами staging, production и archived. У production-модели постоянный URI, по нему загружается последняя версия.

> **Пояснение:** в книге URI выглядит как `models:/{name}/production`. В новом MLflow статусы заменены на alias, поэтому у нас `models:/airbnb-rf@production`.

```python
mv = mlflow.register_model(f"runs:/{run.info.run_id}/model", "airbnb-rf")
client.set_registered_model_alias("airbnb-rf", "production", mv.version)
prod = mlflow.spark.load_model("models:/airbnb-rf@production")
```

```text
registry version: 1 | rows scored: 68
```

### Streaming

Structured Streaming ([глава 8](/book-summaries/engineering/learning-spark/08-structured-streaming/)) считает `inference` на входящих данных непрерывно. Это дороже: ресурсы оплачиваются без перерыва, пропускная способность ниже, а поддерживать и мониторить сложнее.

Код почти не меняется: вместо `spark.read` берут `spark.readStream`. Схему потока задают заранее, даже для Parquet. Мы имитируем поток четырьмя маленькими файлами: `maxFilesPerTrigger=1` даёт по файлу на `micro-batch`.

```python
stream = (spark.readStream.schema(schema).option("maxFilesPerTrigger", 1).parquet(src))
pred = model.transform(stream)        # тот же transform(), что и в batch
pred.writeStream.foreachBatch(show_batch).trigger(availableNow=True).start()
```

```text
batch 0: rows=25, avg pred=187
batch 1: rows=25, avg pred=189
batch 2: rows=25, avg pred=197
batch 3: rows=25, avg pred=194
```

Скрипт: [ch11_stream.py](https://github.com/surfalytics/dataengineer_ru/blob/main/scripts/learning-spark-code/ch11_stream.py). Код одинаков для обоих режимов, поэтому MLlib удобна и для `batch`, и для `streaming`. Но Spark тратит время на план запроса и обмен между `driver` и `executor`, так что для очень низкой задержки модель придётся вынести из Spark.

### Near real-time

Если прогноз нужен за сотни миллисекунд или секунды, можно написать сервер, который считает прогнозы через MLlib. Для Spark это неудачная нагрузка: каждый запрос несёт очень мало данных. Зато задержка ниже, чем у `streaming` и пакетной обработки.

### Экспорт модели для real-time

Настоящий `real-time` нужен, например, для обнаружения мошенничества и рекомендаций рекламы. Сам прогноз по нескольким записям считается быстро. Сложнее другое: балансировка нагрузки (много одновременных запросов) и геолокация, когда важна каждая миллисекунда. Эти задачи решают управляемые сервисы AWS SageMaker и Azure ML, и модель экспортируют туда.

Способы экспорта:

- **Переписать модель вручную.** Коэффициенты достать легко, но вынести весь `feature engineering` (`OneHotEncoder`, `VectorAssembler`) хлопотно и чревато ошибками.
- **MLeap и ONNX** автоматически экспортируют часть моделей MLlib без зависимости от Spark. MLeap уже не поддерживается своей компанией. ONNX стал де-факто открытым стандартом совместимости, а PMML не получил такого признания. Поддержка MLlib в ONNX на момент книги экспериментальная.
- **XGBoost и Sparkling Water** (H2O.ai). XGBoost4J-Spark встраивает распределённый XGBoost в `ML pipeline`. После обучения модель извлекают, сохраняют вне Spark и загружают в Python:

```python
# не запускается: xgboost нет в образе, а распределённый API есть только в Java и Scala
import xgboost as xgb
bst = xgb.Booster({"nthread": 4})
bst.load_model("xgboost_native_model")
```

## Spark без MLlib

MLlib может не уложиться в задержку или не содержать нужный алгоритм. Тогда Spark полезен тремя способами: `inference` для моделей с одной машины, подбор гиперпараметров и масштабирование `feature engineering`.

### Pandas UDF

Типичный случай: модель `scikit-learn` или TensorFlow обучили на одной машине, возможно, на части данных, а применить нужно ко всем. Для этого пишут `UDF` (глава 5), в Python — `pandas UDF` с быстрой сериализацией. Если модель большая, её дорого грузить для каждого пакета. В Spark 3.0 pandas UDF принимает итератор из `pandas.Series` или `pandas.DataFrame`, и модель загружается один раз.

`mapInPandas()` получает итератор `pandas.DataFrame` и возвращает такой же. Он удобен, если модели на вход нужны все колонки, но сериализует весь `DataFrame`. Размер пакета задаёт `spark.sql.execution.arrow.maxRecordsPerBatch`.

```python
def predict(iterator):
    model = mlflow.sklearn.load_model(path)      # модель грузим один раз
    for features in iterator:
        out = pd.DataFrame({"id": features["id"]})
        out["prediction"] = model.predict(features[["bedrooms", "accommodates"]])
        yield out

df.mapInPandas(predict, "id long, prediction double").show()
```

```text
+---+----------+
| id|prediction|
+---+----------+
|  0|     116.9|
|  1|     287.0|
|  2|     205.7|
+---+----------+
```

Три строки из шести. Скрипт: [ch11_pandas_udf.py](https://github.com/surfalytics/dataengineer_ru/blob/main/scripts/learning-spark-code/ch11_pandas_udf.py).

Так же можно параллельно строить много моделей: по одной на тип IoT-устройства, чтобы предсказывать время до отказа. Для этого служит `applyInPandas()`: функция получает `pandas.DataFrame` одной группы и возвращает другой. Две оговорки: `groupBy()` вызывает полный `shuffle`, а модель и данные группы должны помещаться на одной машине. Старый метод `apply()` у сгруппированных данных в будущих версиях Spark объявят устаревшим в пользу `applyInPandas()`.

```python
spark.createDataFrame(dev).groupBy("device_id") \
    .applyInPandas(build_model, schema="device_id string, slope double, n long").show()
```

```text
+---------+-----+---+
|device_id|slope|  n|
+---------+-----+---+
|        a|  2.0| 50|
|        b|  0.5| 50|
+---------+-----+---+
```

### Распределённый подбор гиперпараметров

Даже без распределённого обучения Spark ускоряет подбор гиперпараметров. Авторы показывают две библиотеки.

**Joblib** — набор инструментов для лёгких конвейеров в Python, со Spark-бэкендом. Он рассылает копию данных всем worker, и каждый строит свою модель с другими гиперпараметрами. Предел прежний: одна модель и все данные должны помещаться на одной машине.

![Схема: driver раздаёт наборы гиперпараметров executor, они возвращают loss](/assets/learning-spark/ch11-hyperparam-search.png)

Схема подходит и для Joblib, и для `SparkTrials` из Hyperopt.

Установка: `pip install joblibspark`. Ниже распределённая кросс-валидация, тот же подход работает и для подбора гиперпараметров:

```python
# не запускается: joblibspark нет в образе
from joblibspark import register_spark
register_spark()
gscv = GridSearchCV(rf, {"max_depth": [2, 5, 10], "n_estimators": [20, 50, 100]}, cv=3)
with parallel_backend("spark", n_jobs=3):
    gscv.fit(X_train, y_train)
```

**Hyperopt** — библиотека оптимизации в сложных пространствах поиска. Со Spark её масштабируют двумя способами:

- одиночный Hyperopt с распределённым обучением, например MLlib: настраивать ничего не нужно;
- распределённый Hyperopt с моделями на одной машине, через класс `SparkTrials`. Совместить распределённый подбор и распределённое обучение на момент книги нельзя.

```python
# не запускается: hyperopt нет в образе
best = hyperopt.fmin(fn=training_function, space=search_space, algo=hyperopt.tpe.suggest,
                     max_evals=64, trials=hyperopt.SparkTrials(parallelism=4))
```

`fmin()` создаёт конфигурации для `training_function` и отдаёт их `SparkTrials`. Тот запускает пачки задач параллельно, по одной задаче Spark на `executor`. Результат и loss возвращаются на `driver`, и по ним Hyperopt строит лучшие конфигурации. MLflow записывает все эти модели.

Важен параметр `parallelism` (максимум одновременных испытаний). При `parallelism=1` модели обучаются по очереди, зато адаптивный алгоритм даёт лучшие модели. При `parallelism=max_evals` (общее число моделей) получится случайный поиск. Значения между ними дают компромисс между масштабом и адаптивностью. По умолчанию это число `executor`.

### Koalas

`pandas` работает только на одной машине. Koalas реализует его API поверх Spark: в коде `pd` заменяют на `ks`, не переписывая всё на PySpark. Если функции не хватает, вызывают `kdf.to_spark()`. Вызов `kdf.to_pandas()` собирает все данные на `driver`, и на большом наборе он упадёт.

Тот же пример на `pyspark.pandas`:

```python
import pyspark.pandas as ps
kdf = ps.DataFrame({"duration": [10, 20, 30]})
kdf["duration_new"] = kdf["duration"] + 100
print(kdf.sort_index().to_pandas())
```

```text
   duration  duration_new
0        10           110
1        20           120
2        30           130
```

## Итоги главы

- Воспроизводимость включает код, окружение, данные и саму модель, а не только seed.
- MLflow даёт Tracking, Projects, Models и Registry. Завершённый `run` менять нельзя.
- Режим развёртывания выбирают по задержке, пропускной способности и стоимости до моделирования.
- `Batch` дешевле и проще всего, `streaming` почти не меняет код, но дороже.
- Real-time за миллисекунды MLlib не обеспечивает: модель экспортируют (ONNX, XGBoost) в сервис вроде SageMaker.
- Модели с одной машины масштабируются в Spark через `pandas UDF`, `mapInPandas` и `applyInPandas`.
- Joblib и `SparkTrials` распределяют подбор гиперпараметров, но модель должна помещаться на одной машине.

## Что изменилось к 2026 году

Это наше дополнение, его нет в книге.

- Koalas вошёл в PySpark как `pyspark.pandas` (с Spark 3.2).
- В MLflow 3 вместо статусов Registry используют alias, а файловое хранилище в режиме поддержки: берите базу данных.
- Spark 4.3 требует PyArrow 18 и выше для pandas UDF и `pyspark.pandas`.

## Ключевые термины

| Термин | Значение |
|---|---|
| `run` / `experiment` | Один запуск обучения / группа запусков |
| Model Registry | Хранилище версий модели со статусами или alias |
| `batch` / `streaming` / `real-time` | Прогноз по расписанию / на `micro-batch` / за миллисекунды |
| `SparkTrials` | Класс Hyperopt: испытания идут параллельно на `executor` |

## Что это значит на практике

- Логируйте каждый запуск в Tracking: без `params` и версии кода прошлую модель не повторить.
- Фиксируйте версии библиотек и снимок данных. Одного seed мало.
- Начинайте с `batch`. `Streaming` нужен, когда ожидание в часы уже стоит денег.
- Для задержки в миллисекунды сразу планируйте экспорт модели в сервис вне Spark.

## Практика в DuckDB

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку. Мы моделируем запуски Tracking и Registry таблицами.

### Шаг 1. Создаём данные

```sql
CREATE TABLE runs AS SELECT * FROM (VALUES
    ('r1',  50,  3, 38.2, 0.62),
    ('r2', 100,  5, 30.4, 0.77),
    ('r3', 100, 10, 27.9, 0.81),
    ('r4', 200,  5, 30.1, 0.78),
    ('r5', 200, 10, 27.5, 0.82),
    ('r6',  50, 10, 29.0, 0.80)
) t(run_id, num_trees, max_depth, rmse, r2);

CREATE TABLE registry AS SELECT * FROM (VALUES
    (1, 'r2', 'archived'),
    (2, 'r4', 'staging'),
    (3, 'r5', 'production')
) t(version, run_id, stage);
```

### Шаг 2. Проверяем

Должно быть 6 и 3 строки.

```sql
SELECT (SELECT count(*) FROM runs) AS runs,
       (SELECT count(*) FROM registry) AS versions;
```

### Задания

**1. Лучший запуск.** Найдите запуск с минимальным `rmse`, как делает `search_runs` с сортировкой.

<details><summary>Решение</summary>

```sql
SELECT run_id, num_trees, max_depth, rmse
FROM runs
ORDER BY rmse
LIMIT 1;
```

```text
run_id  num_trees  max_depth  rmse
r5      200        10         27.5
```

Лучший запуск `r5` стоит и в production.

</details>

**2. Что в production.** Покажите параметры и метрики запуска, у которого сейчас статус `production`.

<details><summary>Решение</summary>

```sql
SELECT g.version, r.run_id, r.num_trees, r.max_depth, r.r2
FROM registry g
JOIN runs r USING (run_id)
WHERE g.stage = 'production';
```

```text
version  run_id  num_trees  max_depth  r2
3        r5      200        10         0.82
```

Версия 3 ведёт на запуск `r5`.

</details>

## Вопросы для самопроверки

1. Почему одного `seed` недостаточно для воспроизводимости? Назовите две причины.
2. Когда `batch` лучше `streaming`, и чем платят за низкую задержку?
3. Почему MLlib не годится для real-time за 50 мс, и как вынести модель из Spark?
4. Чем `applyInPandas()` отличается от `mapInPandas()`, и какое у него ограничение?
5. Что меняется в Hyperopt при `parallelism=1` и при `parallelism=max_evals`?

Предыдущая: [Машинное обучение с MLlib](/book-summaries/engineering/learning-spark/10-mllib/). Следующая: [Эпилог: Apache Spark 3.0](/book-summaries/engineering/learning-spark/12-spark-3/).
