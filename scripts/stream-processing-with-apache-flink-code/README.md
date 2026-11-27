# Примеры к книге «Потоковая обработка данных с Apache Flink»

Проверены Flink 1.7.1 для Scala 2.12, JAR авторов со Scala 2.12.8 и Java 8. Раннер использует Docker-образ Maven 3.9.9 с Eclipse Temurin 8 по закреплённому digest. Перед запуском он сверяет контрольные суммы входных файлов. Все задания выполняются в отдельном контейнере с отключённой внешней сетью.

## Запуск

Сохраните [дистрибутив Flink 1.7.1](https://archive.apache.org/dist/flink/flink-1.7.1/flink-1.7.1-bin-scala_2.12.tgz) и [JAR авторов](https://streaming-with-flink.github.io/examples/download/examples-scala.jar) в каталог за пределами репозитория. Для JDBC-примера нужен также [Apache Derby 10.14.2.0](https://repo.maven.apache.org/maven2/org/apache/derby/derby/10.14.2.0/derby-10.14.2.0.jar).

Из корня репозитория выполните команды, подставив каталоги загрузки:

```bash
runner=scripts/stream-processing-with-apache-flink-code/run.sh
archive=/path/to/flink-1.7.1-bin-scala_2.12.tgz
examples=/path/to/examples-scala.jar
derby=/path/to/derby-10.14.2.0.jar

"$runner" "$archive" "$examples"
"$runner" "$archive" "$examples" SensorTotals.java
"$runner" "$archive" "$examples" LateWindow.java
"$runner" "$archive" "$examples" TemperatureChange.java
"$runner" "$archive" "$examples" JdbcRetry.java "$derby"
"$runner" "$archive" "$examples" operations
```

| Глава | Опыт | Проверенный результат |
| --- | --- | --- |
| 1 | Кластер выполняет авторский класс AverageSensorReadings. | В выводе TaskManager появилась строка SensorReading с датчиком, меткой и средней температурой. Значения генерируются случайно. |
| 4 | Архетип Scala 1.7.1 собран командами со страницы главы с Maven 3.9.9 и JDK 8. Для загрузки библиотек нужен доступ к Maven Central. | Создан `target/flink-scala-project-0.1.jar` для Scala 2.12.8. |
| 5 | [SensorTotals.java](SensorTotals.java) накапливает значения по двум ключам. | `(A,2)`, `(B,5)`, `(A,5)`. |
| 6 | [LateWindow.java](LateWindow.java) подаёт события и явные временные отметки в пятисекундное окно. | Первое значение `(A,2)`, уточнение `(A,5)`. |
| 7 | [TemperatureChange.java](TemperatureChange.java) сравнивает каждое измерение с предыдущим для того же датчика. | `A: 20 -> 32`. |
| 8 | [JdbcRetry.java](JdbcRetry.java) записывает значения через JDBC в Derby и повторяет последнюю запись. SQL на странице проверен штатным скриптом и DuckDB CLI 1.4.3. | В Derby осталась строка `A 23`. Два SQL-запроса вернули результаты со страницы. |
| 9–10 | [savepoint.sh](savepoint.sh) проверяет REST, отмену с сохранением и запуск из снимка с другим параллелизмом. | Один TaskManager, два слота. После загрузки снимка новая вершина достигла RUNNING с параллелизмом 2. |

Штатная проверка SQL из корня репозитория:

```bash
python3 -I scripts/book-tools/check_code.py \
  src/content/docs/book-summaries/engineering/stream-processing-with-apache-flink/08-external-systems.md \
  --code-dir scripts/stream-processing-with-apache-flink-code --runner python3 --json
```
