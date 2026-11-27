# Схемы книги

Спецификации находятся в [excalidraw_build.py](excalidraw_build.py). Для рендера запустите адаптер по [инструкции](../book-tools/README.md#excalidraw-for-codex), затем выполните из корня репозитория:

```sh
python3 scripts/stream-processing-with-apache-flink-diagrams/excalidraw_build.py
```

Каждая сцена сохраняется под именем `dataengineer_ru/flink-<имя PNG без расширения>`.

| Глава | Источник в книге | Что показывает схема | PNG |
|---|---|---|---|
| 0 | Карта книги | Порядок глав и четыре темы | [book-map.png](../../public/assets/stream-processing-with-apache-flink/book-map.png) |
| 1 | 1.4–1.6 | Два независимых приложения читают журнал | [ch01-event-log.png](../../public/assets/stream-processing-with-apache-flink/ch01-event-log.png) |
| 1 | 1.7 | Быстрая ветвь и пакетный пересчёт | [ch01-lambda.png](../../public/assets/stream-processing-with-apache-flink/ch01-lambda.png) |
| 2 | 2.11–2.13 | Часы устройства и время получения записи | [ch02-two-clocks.png](../../public/assets/stream-processing-with-apache-flink/ch02-two-clocks.png) |
| 3 | 3.1–3.2 | Роли в работающем кластере | [ch03-job.png](../../public/assets/stream-processing-with-apache-flink/ch03-job.png) |
| 3 | 3.8–3.9 | Минимум входных отметок времени | [ch03-watermarks.png](../../public/assets/stream-processing-with-apache-flink/ch03-watermarks.png) |
| 3 | 3.17–3.25 | Выравнивание двух входов в согласованном снимке | [ch03-barrier.png](../../public/assets/stream-processing-with-apache-flink/ch03-barrier.png) |
| 5 | 5.4 | Накопленный итог по ключу | [ch05-keyed-sum.png](../../public/assets/stream-processing-with-apache-flink/ch05-keyed-sum.png) |
| 6 | 6.1–6.3 | Фиксированные, перекрывающиеся и сессионные окна | [ch06-window-types.png](../../public/assets/stream-processing-with-apache-flink/ch06-window-types.png) |
| 6 | 6.7–6.8 | Часовая граница разделяет близкие события | [ch06-joins.png](../../public/assets/stream-processing-with-apache-flink/ch06-joins.png) |
| 6 | Раздел 6.5 | Первый ответ, уточнение и очистка | [ch06-late-window.png](../../public/assets/stream-processing-with-apache-flink/ch06-late-window.png) |
| 7 | Раздел 7.3 и рис. 3.13 | Перераспределение групп ключей | [ch07-key-groups.png](../../public/assets/stream-processing-with-apache-flink/ch07-key-groups.png) |
| 7 | 7.1 | Внешний запрос состояния по ключу | [ch07-query.png](../../public/assets/stream-processing-with-apache-flink/ch07-query.png) |
| 8 | 8.1 | Смещение хранится отдельно для каждой партиции | [ch08-kafka-offsets.png](../../public/assets/stream-processing-with-apache-flink/ch08-kafka-offsets.png) |
| 8 | Раздел 8.4.2 | Подготовка и фиксация внешней транзакции | [ch08-two-phase.png](../../public/assets/stream-processing-with-apache-flink/ch08-two-phase.png) |
| 9 | Раздел 9.2 и рис. 3.3 | Координаторы, ZooKeeper и общее хранилище | [ch09-ha.png](../../public/assets/stream-processing-with-apache-flink/ch09-ha.png) |
| 10 | Раздел 10.1.2 | Остановка с сохранением и повторный запуск | [ch10-resume.png](../../public/assets/stream-processing-with-apache-flink/ch10-resume.png) |
