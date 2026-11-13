| Глава | Figure | Идея | Наш файл | Статус |
|---|---|---|---|---|
| 1 | 1.1, 1.2 | Погодный pipeline и его граф | текст страницы (три шага) | skipped: простая цепочка, описана словами и показана в ch01-execution-loops.png |
| 1 | 1.3 | DAG и граф с циклом | ch01-dag-vs-cycle.png | redrawn (ch01_diagrams.py) |
| 1 | 1.4 | Три прохода алгоритма выполнения | ch01-execution-loops.png | redrawn (ch01_diagrams.py) |
| 1 | 1.5, 1.6 | Граф pipeline для прогноза спроса на зонты | ch01-umbrella-dag.png | redrawn (specs/ch01.py) |
| 1 | 1.7 | DAG file, расписание, граф | текст страницы + код ch01_weather_dag.py | skipped: показан кодом |
| 1 | 1.8, 1.9 | Компоненты Airflow и цикл scheduler | ch01-airflow-components.png | redrawn (specs/ch01.py); цикл дан списком из пяти шагов |
| 1 | 1.10-1.14 | Скриншоты веб-интерфейса | нет | skipped: скриншоты интерфейса, описаны словами |
| 2 | 2.1, 2.3 | Ментальная модель Джона и три tasks | ch02-rocket-dag.png | redrawn (specs/ch02.py) |
| 2 | 2.2, 2.12 | Пример картинки ракеты и папка с картинками | нет | skipped: фотографии, не схема |
| 2 | 2.4 | Explicit definition и context manager | таблица на странице | skipped: показано таблицей |
| 2 | 2.5 | DAG, task и operator | ch02-dag-task-operator.png | redrawn (ch02_diagrams.py) |
| 2 | 2.6 | python_callable указывает на функцию | текст страницы | skipped: описано словами |
| 2 | 2.7-2.11, 2.13 | Скриншоты UI: список DAG, graph view, логи, grid view | нет | skipped: скриншоты интерфейса, описаны словами |
| 2 | 2.14-2.18 | Сбой, stack trace, clear, восстановление | ch02-failure-clear.png | redrawn (specs/ch02.py) |
| 2 | 2.19-2.21 | DAG versioning: версии v1 и v2 | ch02-dag-versions.png | redrawn (ch02_diagrams.py) |
| 3 | 3.1, 3.3, 3.4 | Расписание между start_date и end_date | - | skipped: простая линия времени, текст объясняет |
| 3 | 3.2, 3.9 | catchup=False и catchup=True | - | skipped: описано в тексте, нет потока |
| 3 | 3.5 | Инкремент: файлы по дням | ch03-incremental-partitions.png | redrawn (specs/ch03.py) |
| 3 | 3.6 | Trigger и interval | ch03-trigger-vs-interval.png | redrawn (specs/ch03.py) |
| 3 | 3.7, 3.8 | Интервалы, run в конце интервала | ch03-interval-timeline.png | redrawn (ch03_diagrams.py) |
| 3 | 3.10 | Атомарность | ch03-atomicity.png | redrawn (ch03_diagrams.py) |
| 3 | 3.11 | Идемпотентность | - | skipped: показано кодом ch03_idempotent.py с выводом |
| 4 | Figure 4.1 | Каждая команда качает сама и central producer | ch04-asset-flow.png | redrawn (старая схема, переиспользована) |
| 4 | Figure 4.2, 4.3 | Producer, asset, consumers | ch04-asset-flow.png | redrawn (та же схема) |
| 4 | Figure 4.4-4.7, 4.9, 4.10 | Скриншоты UI Airflow | - | skipped: скриншоты |
| 4 | Figure 4.8, 4.11 | Два producer и один consumer, события обоих assets | ch04-multi-assets.png | redrawn (старая схема, переиспользована) |
| 5 | 5.1, 5.2 | Скачивание и первый анализ данных Wikimedia | текст страницы | skipped: команды shell, описаны словами |
| 5 | 5.3, 5.12 | Шаги StockSense | ch05-stocksense-hook.png | redrawn (ch05_diagrams.py) |
| 5 | 5.4 | Строка с `{{ name }}` и подстановка | ch05-context-flow.png | redrawn (specs/ch05.py), идея объяснена текстом |
| 5 | 5.5 | Context как словарь в PythonOperator | ch05-context-flow.png | redrawn (specs/ch05.py); полный список в таблице страницы |
| 5 | 5.6-5.9 | Как Python раздаёт аргументы функции | ch05-kwargs-routing.png | redrawn (ch05_diagrams.py) |
| 5 | 5.10 | output_path через аргумент | текст страницы | skipped: описано в разделе про op_args и op_kwargs |
| 5 | 5.11, 5.14 | Скриншоты Rendered Template и Connections | нет | skipped: скриншоты интерфейса, описаны словами |
| 5 | 5.13 | Граф DAG StockSense | ch05-stocksense-hook.png | redrawn (ch05_diagrams.py) |
| 5 | 5.15 | Operator, hook и база | ch05-stocksense-hook.png | redrawn (ch05_diagrams.py) |
| 6 | Figure 6.1 | Линейный DAG с ракетами | - | skipped: повтор схемы главы 2 |
| 6 | Figure 6.2, 6.3, 6.4 | Umbrella DAG, fan-out, fan-in, порядок выполнения | ch06-fanout-fanin.png | redrawn |
| 6 | Figure 6.5, 6.7, 6.9, 6.10 | Две ERP, ветка в DAG, join после ветки | ch06-branching.png | redrawn (старая схема, переиспользована) |
| 6 | Figure 6.6, 6.11, 6.13, 6.16, 6.17 | Скриншоты UI Airflow | - | skipped: скриншоты |
| 6 | Figure 6.8, 6.14, 6.15 | Trigger rules и propagation | ch06-trigger-rules.png | redrawn (старая схема, переиспользована) |
| 6 | Figure 6.12 | DAG с условной задачей latest_only | - | skipped: описано в тексте |
| 6 | Figure 6.18, 6.19 | Taskflow и XCom | ch06-xcom-taskflow.png | redrawn |
| 7 | общая схема | Четыре способа запустить DAG | ch07-triggers.png | redrawn (specs/ch07.py) |
| 7 | 7.1 | Начальная логика DAG супермаркетов | нет | skipped: просто описана в тексте |
| 7 | 7.2-7.4 | Запуск в 02:00 и ожидание против sensors | ch07-wait-timeline.png | redrawn |
| 7 | 7.5, 7.6 | DAG с sensors, UI | нет | skipped: скриншоты UI |
| 7 | 7.7 | Sensors падают по timeout | нет | skipped: скриншот UI |
| 7 | 7.8-7.10 | Sensor deadlock, reschedule, deferrable | ch07-slots.png | redrawn (одна схема) |
| 7 | 7.11 | DAG с conf и без conf | нет | skipped: идея в тексте, схема не нужна |
| 7 | 7.12 | DAG от сообщений Kafka | ch07-kafka-asset.png | redrawn |
| 8 | 8.1 | Operator переводит аргументы в вызовы клиента (Cloud SDK) | нет | skipped: идея описана в тексте, рисунок из двух блоков |
| 8 | 8.2 | Примеры цифр MNIST | нет | skipped: иллюстрация данных |
| 8 | 8.3 | Offline: обучение, online: классификация | ch08-ml-pipeline.png | redrawn (вместе с 8.5, 8.10) |
| 8 | 8.4, 8.5 | Шаги pipeline: копия, преобразование, обучение, деплой | ch08-ml-pipeline.png | redrawn |
| 8 | 8.6, 8.7, 8.9 | Скриншоты S3 и SageMaker | нет | skipped: скриншоты консоли AWS |
| 8 | 8.8 | wait_for_completion: task успешна, когда job закончилась | ch08-wait-completion.png | redrawn (новая) |
| 8 | 8.10 | Airflow DAG и разовый деплой Lambda + API Gateway | ch08-ml-pipeline.png | redrawn |
| 8 | 8.11 | Пример запроса и ответа API | нет | skipped: пример вывода |
| 8 | 8.12 | Airflow двигает данные между системами | ch08-orchestration-execution.png, ch08-a-to-b.png | redrawn |
| 8 | 8.13 | Структура таблицы Inside Airbnb | нет | skipped: схема таблицы без идеи |
| 8 | 8.14 | Экспорт в строки кортежей | нет | skipped: описано в тексте и в задании 1 |
| 9 | 9.1 | Пилот: API, fetch, rank, recommender | текст страницы | skipped: простая цепочка, описана словами |
| 9 | 9.2-9.4, 9.8 | Скриншоты API и интерфейса | нет | skipped: скриншоты, описаны словами |
| 9 | 9.5 | Форма Connection в интерфейсе | нет | skipped: скриншот, шаги в тексте |
| 9 | (слои) | DAG, operator, sensor, hook, Connection, API | ch09-layers.png | redrawn (specs/ch09.py) |
| 9 | 9.6 | Worker slots: обычный и deferrable подход | ch09-worker-slots.png | redrawn (ch09_diagrams.py) |
| 9 | 9.7 | Последовательность deferrable sensor | ch09-deferrable.png | redrawn (specs/ch09.py) |
| 9 | (пакет) | Пакет ставят во все окружения Airflow | ch09-package.png | own diagram (ch09_diagrams.py) |
| 10 | 10.1 | Ошибка цикла DAG в интерфейсе | нет | skipped: скриншот UI |
| 10 | 10.2, 10.3 | Структура пакета и папки tests/ | нет | skipped: описано текстом |
| 10 | 10.4, 10.5 | DAG_PATH и parametrize | нет | skipped: объяснено в тексте |
| 10 | 10.6 | Свойства mock (скриншот PyCharm) | ch10-where-to-patch.png | redrawn: идея про место патча |
| 10 | 10.7 | JSON в CSV | нет | skipped: пример данных |
| 10 | 10.8 | Разбор INSERT-запросов | нет | skipped: детали кода |
| 10 | 10.9 | Жизненный цикл контейнера в pytest | ch10-mock-or-docker.png | redrawn (старая диаграмма, specs/ch10.py) |
| 10 | 10.10-10.13 | Скриншоты отладчика PyCharm, pdb | нет | skipped: скриншоты |
| 10 | новая | CI/CD pipeline | ch10-ci-pipeline.png | старая диаграмма, specs/ch10.py |
| 10 | новая | Три способа проверить весь DAG | ch10-whole-dag.png | новая |
| 11 | 11.1 | DAG рекомендаций: три задачи, три оператора | нет | skipped: описано в тексте |
| 11 | 11.2, 11.6 | Конфликт версий библиотек в одном окружении и изоляция в контейнерах | ch11-dependencies.png | redrawn (новая) |
| 11 | 11.3 | VM и контейнеры | нет | skipped: сравнение описано в тексте |
| 11 | 11.4, 11.8, 11.11 | Вывод контейнера wttr, скриншоты UI Airflow | нет | skipped: скриншоты и вывод |
| 11 | 11.5 | Рекомендательный DAG на DockerOperator | нет | skipped: описано в тексте |
| 11 | 11.7, 11.9 | Что происходит при запуске DockerOperator; процесс работы с образами | ch11-container-workflow.png | redrawn (старая, specs/ch11.py) |
| 11 | 11.10 | Kubernetes: master, nodes, pods | ch11-docker-vs-k8s.png | redrawn частично: описано в тексте |
| 11 | 11.12 | Процесс работы с KubernetesPodOperator | ch11-docker-vs-k8s.png | redrawn (старая, specs/ch11.py) |
| 12 | (parse vs run) | Код DAG парсится часто, тяжёлая работа внутри задач | ch12-parse-vs-run.png | redrawn (specs/ch12.py) |
| 12 | 12.1, 12.2 | Задачи из фабрики, DAG из фабрики | текст страницы | skipped: простая идея, описана словами |
| 12 | 12.3, 12.4 | Task groups в интерфейсе | текст страницы | skipped: скриншоты |
| 12 | 12.5-12.8 | Dynamic Task Mapping: expand, grid и graph view | ch12-dynamic-mapping.png | redrawn (specs/ch12.py); скриншоты skipped |
| 12 | 12.9 | Join потом фильтр и фильтр потом join | ch12-early-filter.png | redrawn (ch12_diagrams.py) |
| 12 | 12.10, 12.11 | Монолитная и инкрементальная обработка, кэш промежуточных данных | текст страницы | skipped: описано словами |
| 12 | 12.12 | Форма pool в интерфейсе | ch12-pool-slots.png | own diagram (ch12_diagrams.py), скриншот skipped |
| 13 | 13.1 | Блоки проекта: два источника, MinIO, PostgreSQL, веб-страница | ch13-nyc-pipeline.png | redrawn (specs/ch13.py) |
| 13 | 13.2, 13.3 | Карта зон и станций, привязка станций к зонам | текст страницы | skipped: карты, описаны словами |
| 13 | 13.4, 13.5, 13.7 | Extras S3 connection, скриншоты MinIO | текст страницы | skipped: скриншоты, описаны словами |
| 13 | 13.6 | Два tasks скачивания | текст страницы + ch13_nyc_dag.py | skipped: показано кодом |
| 13 | (код 13.11-13.15) | PandasOperator: input, transform, output | ch13-pandas-operator.png | redrawn (ch13_diagrams.py) |
| 13 | 13.8 | Слои raw, processed, export | таблица на странице | skipped: показано таблицей |
| 13 | (код 13.16-13.17) | Запись без защиты и DELETE + INSERT | ch13-idempotent-write.png | redrawn (specs/ch13.py) |
| 13 | 13.9 | Веб-страница с результатом | текст страницы | skipped: скриншот |
| 14 | 14.15 | DAG загрузки | ch14-ingestion-dag.png | redrawn (старая, specs/ch14.py) |
| 14 | 14.3, 14.18 | RAG-процесс | ch14-rag-flow.png | redrawn (старая, specs/ch14.py) |
| 14 | 14.1, 14.2, 14.16 | Пространство вкусов, cosine similarity | ch14-flavor-space.png | redrawn (ch14_diagrams.py) |
| 14 | 14.10-14.12 | Три случая compare_objects | ch14-compare-cases.png | redrawn (ch14_diagrams.py) |
| 14 | 14.4 | Архитектура проекта | нет | merged: таблица сервисов и ch14-ingestion-dag.png |
| 14 | 14.5, 14.6, 14.14, 14.19, 14.20 | Скриншоты UI, MinIO, Weaviate | нет | skipped: скриншоты |
| 14 | 14.7, 14.9, 14.13 | DataFrame и chunks, dict | нет | skipped: описано текстом |
| 14 | 14.8 | UUID двух чизкейков | нет | skipped: описано текстом, вывод в практике |
| 14 | 14.17 | Retrieval | ch14-rag-flow.png | merged |
| 15 | 15.1 | Компоненты Airflow | таблица на странице | skipped: показана в главе 1, описана таблицей |
| 15 | (обзор) | Четыре executors | ch15-executors.png | redrawn (specs/ch15.py) |
| 15 | 15.2, 15.3, 15.5, 15.6 | Local, Celery, Kubernetes, Edge: схемы развёртывания | ch15-executors.png | merged в одну общую схему |
| 15 | 15.4, 15.9, 15.11-15.16 | Flower, Grafana, Prometheus, письмо | текст страницы | skipped: скриншоты |
| 15 | 15.7 | Примеры DAG в интерфейсе | текст страницы | skipped: скриншот |
| 15 | 15.8 | Путь task: scheduled, queued, running, success | ch15-task-states.png | redrawn (ch15_diagrams.py) |
| 15 | 15.10 | Airflow, StatsD exporter, Prometheus, Grafana | ch15-metrics-stack.png | redrawn (specs/ch15.py) |
| 15 | (таблица 15.2) | Лимиты параллелизма | ch15-concurrency-limits.png | own diagram (ch15_diagrams.py) |
| 15 | 15.17, 15.18 | Общий Airflow и Airflow на команду | таблица на странице | skipped: сравнение дано таблицей |
| 16 | 16.1, 16.2 | RBAC: пользователь, роль, право, компонент UI | таблица ролей на странице | skipped: показано таблицей |
| 16 | 16.3-16.5 | Скриншоты Security view, ролей, темы | текст страницы | skipped: скриншоты |
| 16 | 16.6, 16.7 | Точки входа в Airflow, Fernet key шифрует и расшифровывает | ch16-security-layers.png | redrawn (specs/ch16.py, общая схема слоёв) |
| 16 | 16.8 | LDAP: пользователи в каталоге | ch16-security-layers.png | redrawn (specs/ch16.py) |
| 16 | 16.9 | Дерево каталога DIT и запись Боба | ch16-ldap-dit.png | redrawn (ch16_diagrams.py) |
| 16 | 16.10, 16.11 | MITM-атака, HTTP без проверки | текст страницы | skipped: описаны словами |
| 16 | 16.12, 16.13, 16.17 | Предупреждения браузера | текст страницы | skipped: скриншоты |
| 16 | 16.14 | Рукопожатие HTTPS | ch16-https-handshake.png | redrawn (ch16_diagrams.py) |
| 16 | 16.15 | Symmetric и asymmetric encryption | таблица на странице | skipped: показано таблицей |
| 16 | 16.16, 16.18, 16.19 | UI по HTTPS, добавление certificate в macOS | текст страницы | skipped: скриншоты |
| 16 | 16.20, 16.21 | Секрет в Vault и ключ conn_uri | ch16-secrets-lookup.png + текст | skipped: скриншоты Vault; порядок поиска redrawn (specs/ch16.py) |
| 17 | 17.1 | Astronomer UI: обзор deployments | нет | skipped: скриншот интерфейса, описан словами |
| 17 | 17.2 | Кластер Kubernetes и внешние сервисы | ch17-deploy-choice.png | redrawn (specs/ch17.py): общий выбор пути и шаги Helm |
| 17 | 17.3 | Архитектура Airflow с CeleryExecutor | текст страницы (таблица pods) | skipped: уже в главе 1 (ch01-airflow-components.png), pods даны таблицей |
| 17 | 17.4-17.8 | Скриншоты DAG из image, volume, Git, зависимостей | ch17-dag-delivery.png | redrawn (specs/ch17.py): три способа доставки, скриншоты skipped |
| 17 | 17.9, 17.10 | Две tasks на KubernetesExecutor и одна на Celery | ch17-multi-executor.png | redrawn (ch17_diagrams.py) |
| 17 | наша | Values-файлы накапливают правки | ch17-values-layers.png | own (ch17_diagrams.py) |
