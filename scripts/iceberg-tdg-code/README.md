# Примеры к Apache Iceberg: The Definitive Guide

| Глава | Файл | Что проверено |
|---|---|---|
| 1 | [ch01_table_state.py](ch01_table_state.py) | Два состояния учебного списка файлов, Python 3. |
| 2 | [ch02_pruning.py](ch02_pruning.py) | Отсечение файлов по границам значений, Python 3. |
| 3, 10 | [table_history.py](table_history.py) | PyIceberg создаёт две версии таблицы и читает каждую. |
| 3, 4 | [spark_table.py](spark_table.py) | Spark выполняет MERGE, читает исторический snapshot и вызывает rewrite_data_files. |
| 5, 6 | [register_table.py](register_table.py) | Spark создаёт таблицу с разбиением и регистрирует её в другом каталоге. |
| 9, 11 | [flink_batch.sql](flink_batch.sql) | Flink создаёт каталог, таблицу и читает записанную строку. Потоковое чтение той же таблицы разобрано в главе 11. |
| 13 | [snapshot_migration.py](snapshot_migration.py) | Обе таблицы возвращают по две строки и используют те же файлы Parquet. |
| 14 | [branch_publish.py](branch_publish.py) | Запись в ветку, проверка суммы заказа и публикация в main. |

## Запуск

Команды приведены для корня репозитория. Скрипты Python и Spark создают временное хранилище. Для PyIceberg потребуется Python 3.12 и зависимости из файла рядом со скриптом.

```sh
python3 scripts/iceberg-tdg-code/ch01_table_state.py
python3 scripts/iceberg-tdg-code/ch02_pruning.py
python3.12 -m venv .venv
.venv/bin/pip install -r scripts/iceberg-tdg-code/requirements.txt
.venv/bin/python scripts/iceberg-tdg-code/table_history.py
```

Для Spark использованы версия 3.5.5, Scala 2.12, Java 17 и Iceberg 1.8.1. JDBC-пример использует SQLite. Одна и та же команда запускает любой из четырёх Spark-скриптов при подстановке имени файла.

```sh
spark-submit --packages org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.8.1,org.xerial:sqlite-jdbc:3.47.1.0 scripts/iceberg-tdg-code/register_table.py
```

Для Flink SQL использованы Flink 1.20.5, iceberg-flink-runtime-1.20 версии 1.8.1, hadoop-client-api и hadoop-client-runtime версии 3.3.6 и commons-logging 1.2. В изолированном локальном кластере с этими библиотеками выполните SQL через клиент. Файл использует каталог в /tmp/iceberg-warehouse. При повторном запуске выберите новую директорию для warehouse.

```sh
bin/sql-client.sh -f scripts/iceberg-tdg-code/flink_batch.sql
```

В главах 7 и 12 приведён синтаксис Dremio, который требует настроенного источника и соответствующих прав. В главе 8 приведён пример для AWS Glue с доступом к AWS Glue Data Catalog и S3. Для этих примеров на страницах указаны условия запуска.
