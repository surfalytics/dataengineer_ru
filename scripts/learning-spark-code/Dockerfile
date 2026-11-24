# Образ для всех примеров конспекта Learning Spark.
# Python 3.12 + Java 17 + PySpark 4.3.0 (Spark 4.3 требует Java 17+ и Python 3.11+).
# Сборка: docker build -t learning-spark:4.3.0 scripts/learning-spark-code
FROM python:3.12-slim-bookworm
RUN apt-get update \
 && apt-get install -y --no-install-recommends openjdk-17-jre-headless procps \
 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
ENV PYSPARK_PYTHON=python3
RUN useradd -m spark
USER spark
