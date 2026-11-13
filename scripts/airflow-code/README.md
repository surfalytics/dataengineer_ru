# Код к конспекту Data Pipelines with Apache Airflow

Проверено на Airflow 3.4.0, DAG-и без запущенного сервера (`DagBag`, `airflow dags test`).
Запуск из корня репозитория: `python3 -I scripts/airflow-code/<файл>.py`. Для DAG-файлов нужен venv с `apache-airflow==3.4.0` и провайдерами (kafka, amazon, postgres, http, cncf-kubernetes). Полный `requirements.txt` ещё не собран: версии видны в строках таблицы.
Страницы собираются командой `python3 scripts/airflow-code/embed.py <шаблон.md> <страница.md>`.

| Глава | Пример | Файл | Статус |
|---|---|---|---|
| 1 | Алгоритм выполнения графа зонтов, чистый Python | ch01_execute_graph.py | ok (6 запусков `python3 -I`, вывод одинаков) |
| 1 | DAG погодного дашборда | ch01_weather_dag.py | ok: DagBag без ошибок, `airflow dags test weather_board 2026-01-02` завершился state=success (Airflow 3.4.0) |
| 1 | Проверка DAG через DagBag | ch01_check_weather_dag.py | ok (6 запусков `$VENV/bin/python -I`, вывод одинаков) |
| 2 | DAG про запуски ракет (версия без сети: JSON пишет первая task) | ch02_rocket_dag.py | ok: DagBag без ошибок, `dag.test()` завершился, три tasks в `success` (Airflow 3.4.0) |
| 2 | Проверка DAG через DagBag и `dag.test()` | ch02_check_rocket.py | ok (6 запусков `python -I`, вывод одинаков) |
| 2 | DAG, где get_pictures падает | ch02_failure_dag.py | ok: через ch02_failure_demo.py |
| 2 | Статусы при сбое: failed и upstream_failed | ch02_failure_demo.py | ok (6 запусков `python -I`, вывод одинаков) |
| 2 | Запуск через Docker Compose, `docker exec`, скачивание картинок из Launch Library API | нет | не запускали: нужны Docker и сеть, в книге это шаги установки |
| 3 | Три расписания: когда стартует run, какой интервал | ch03_timetables.py | ok (6 запусков `$VENV/bin/python -I`, вывод одинаков, Airflow 3.4.0) |
| 3 | DAG событий: data interval по дням, partitions, перезапись | ch03_events_dag.py | ok: DagBag без ошибок, `airflow dags test events_daily 2025-01-01` завершился state=success (Airflow 3.4.0). API из книги заменён функцией, сеть не нужна |
| 3 | Идемпотентность: дописывать и перезаписывать | ch03_idempotent.py | ok (6 запусков `python3 -I`, вывод одинаков) |
| 4 | Producer, consumer, два assets, пропуск обновления | ch04_asset_dags.py | ok: DagBag без ошибок (Airflow 3.4.0) |
| 4 | Проверка: DagBag + `airflow dags test` producer + события | ch04_check_asset_dags.py | ok (6 запусков `python3 -I` из venv, вывод одинаков). Сам consumer не запускали: его запускает scheduler по событию |
| 5 | DAG StockSense: templating в BashOperator и PythonOperator (URL только печатается) | ch05_stocksense_dag.py | ok: DagBag без ошибок, `airflow dags test stocksense_templating 2025-04-24T22:00:00` завершился state=success (Airflow 3.4.0) |
| 5 | Проверка DAG: DagBag и `airflow tasks render` | ch05_check_render.py | ok (6 запусков `$VENV/bin/python -I`, вывод одинаков). Нужен Airflow и AIRFLOW_HOME |
| 5 | Идемпотентная запись, upsert в sqlite3 | ch05_idempotent_insert.py | ok (6 запусков `python3 -I`, вывод одинаков) |
| 5 | Скачивание файла Wikimedia, запись в PostgreSQL через SQLExecuteQueryOperator | нет | не запускали: нужны сеть и PostgreSQL (Docker). На странице есть только описание |
| 6 | umbrella DAG: fan-out, ветка по ERP, join, LatestOnlyOperator, Taskflow XCom | ch06_branch_dag.py | ok: DagBag без ошибок, `dag.test()` для двух дат (Airflow 3.4.0) |
| 6 | trigger rules: all_success, none_failed, all_done, one_failed на статусах success, skipped, failed | ch06_trigger_rules_dag.py | ok: `dag.test()`, статусы на странице настоящие |
| 6 | Проверка: копирует DAG во временный AIRFLOW_HOME, `dag.test()`, печать статусов | ch06_check.py | ok (6 запусков `python -I` из venv, вывод одинаков). `dag.test()` это ручной запуск, поэтому LatestOnlyOperator его не пропускает |
| 7 | PythonSensor с двумя условиями (данные и маркер `_DONE`), `mode="reschedule"` | ch07_sensor_dag.py, ch07_batch_ready.py | ok: DagBag без ошибок (Airflow 3.4.0). Сам sensor с настоящими папками не запускали |
| 7 | Логика `batch_is_ready` и расчёт sensor deadlock | ch07_check_sensor.py | ok (6 запусков `python3 -I`, вывод одинаков) |
| 7 | DAG с `dag_run.conf`, `schedule=None` | ch07_conf_dag.py | ok: `airflow dags test ch07_conf_demo --conf '{"supermarket_id": 1}'` state=success, run_type=manual. Без `--conf` task падает с KeyError |
| 7 | DAG от сообщения Kafka: MessageQueueTrigger + AssetWatcher | ch07_kafka_dag.py | частично: DagBag разбирает без ошибок. Не запускали: нужен брокер Kafka |
| 7 | Проверка обоих DAG через DagBag | ch07_check_dags.py | ok. Нужны Airflow, `apache-airflow-providers-apache-kafka==3.0.0`, `apache-airflow-providers-common-messaging==2.1.2` |
| 7 | Запуск через REST API (curl), CLI `dags trigger` | нет | не запускали: нужен работающий api-server. На странице только описание |
| 8 | DAG обучения в SageMaker (сокращённый): S3CopyObjectOperator и SageMakerTrainingOperator | ch08_sagemaker_dag.py | ok: DagBag без ошибок (Airflow 3.4.0, providers amazon 9.40.0). В AWS не ходит |
| 8 | Проверка DAG и имён training job | ch08_check_dag.py | ok (6 запусков `$VENV/bin/python -I`, вывод одинаков) |
| 8 | Свой A-to-B operator: PostgreSQL в CSV на S3 | ch08_orders_to_s3.py | ok: проверен с mock вместо hooks (provider postgres 7.1.2) |
| 8 | Проверка operator без PostgreSQL и S3 | ch08_check_operator.py | ok (6 запусков `$VENV/bin/python -I`, вывод одинаков) |
| 8 | Полный DAG MNIST, SageMakerEndpointOperator, Chalice API, DockerOperator, MinIO | нет | не запускали: нужны аккаунт AWS, Docker и данные Inside Airbnb. На странице есть только описание |
| 9 | Hook, operator, sensor, trigger, deferrable sensor для выдуманного API заказов | ch09_components.py | ok (классы проверяет ch09_check.py) |
| 9 | Проверка без сервера: пагинация, шаблоны, poke, defer, trigger, DagBag | ch09_check.py | ok (6 запусков `$VENV/bin/python -I`, вывод одинаков). API и Connection заменены заглушками |
| 9 | DAG с sensor, deferrable sensor и fetch | ch09_dag.py | ok: DagBag без ошибок. `airflow dags test` не запускали: нужен живой API |
| 9 | Реальный triggerer, Docker Compose с MovieLens API, `setup.py` и `pip install` пакета | нет | не запускали: нужны Docker, сеть и живой triggerer |
| 10 | DAG integrity test и проверка на четырёх тестовых DAG | ch10_integrity_test.py | ok: Airflow 3.4.0, pytest 9.2.0; 6 запусков `python -I`, вывод одинаков |
| 10 | Unit-тест оператора с mock | ch10_operator_test.py | ok: 6 запусков `python -I`, вывод одинаков; проходит и в pytest |
| 10 | Решения заданий 1-3 (правило имён, tmp_path, патч на классе hook) | ch10_practice_test.py | ok: 3 теста проходят в pytest |
| 10 | Тест с контейнером PostgreSQL (`pytest-docker-tools`), Whirl, DTAP, GitHub Actions | нет | не запускали: нужны Docker и GitHub. Код CI на странице только как пример |
| 10 | `dag.test()` | нет | не запускали: книга сообщает об ошибке в Airflow 3.1 |
| 11 | CLI-скрипт рейтинга фильмов (click) | ch11_rank_movies.py | ok: запущен через CliRunner (click 8.5.1) |
| 11 | DAG на DockerOperator | ch11_docker_dag.py | ok: DagBag без ошибок. Не запускали: нет Docker |
| 11 | DAG на KubernetesPodOperator | ch11_k8s_dag.py | ok: DagBag без ошибок. Не запускали: нет кластера Kubernetes |
| 11 | Проверка CLI и разбор DAG | ch11_check.py | ok (6 запусков `$VENV/bin/python -I`, вывод одинаков) |
| 11 | Dockerfile из задания, `docker build`, `kubectl apply`, YAML ресурсов | нет | не запускали: нужны Docker и Kubernetes |
| 12 | Dynamic Task Mapping, pool, явный timetable | ch12_mapping_dag.py | ok: DagBag без ошибок, `airflow dags test reviews_mapping 2025-01-02` завершился успешно (3 экземпляра print_rating, Airflow 3.4.0). API заменён функцией |
| 12 | Фабрика задач, фабрика DAG, `globals()`, TaskGroup | ch12_factory_dag.py | ok: DagBag без ошибок. Не запускали: команды BashOperator только печатают |
| 12 | Connection внутри task, а не в теле файла | ch12_light_task.py | ok: импорт проходит. Не запускали: нужен connection `my_api` |
| 12 | Проверка без сервера: DagBag, mapped, pool, timetable | ch12_check.py | ok (6 запусков `$VENV/bin/python -I`, вывод одинаков, Airflow 3.4.0) |
| 12 | Порядок set зависит от hash seed, sorted и seed | ch12_deterministic.py | ok (6 запусков `python3 -I`, вывод одинаков) |
| 13 | PandasOperator из книги: CSV такси, transform, вывод в буфер (MinIO заменён памятью) | ch13_pandas_operator.py | ok (6 запусков `$VENV/bin/python -I`, вывод одинаков; Airflow 3.4.0, pandas 2.3.3) |
| 13 | Запись в базу: append даёт дубли, DELETE + INSERT в транзакции нет (SQLite) | ch13_idempotent_write.py | ok (6 запусков, вывод одинаков; pandas 2.3.3, sqlalchemy 2.1.8) |
| 13 | Каркас DAG nyc_dag (скачивание Citi Bike и такси в MinIO) | ch13_nyc_dag.py, ch13_check.py | только DagBag: ошибок нет, 2 tasks. Скачивание не запускали: нужны Docker Compose книги, MinIO и оба API |
| 14 | DAG загрузки на DockerOperator (5 tasks, общие параметры) | ch14_ingestion_dag.py | ok: DagBag без ошибок. Не запускали: нет Docker, Weaviate и MinIO |
| 14 | Проверка DAG: порядок tasks и команда compare | ch14_check.py | ok (6 запусков `$VENV/bin/python -I`, вывод одинаков) |
| 14 | RAG без платных API: chunks, uuid5, compare, поиск cosine, prompt | ch14_recipe_vault_local.py | ok: только стандартная библиотека, 6 запусков `python3 -I`, вывод одинаков |
| 14 | Создание collection Weaviate с OpenAI embeddings, LangChain-цепочка | нет (блок на странице) | не запускали: нужны Weaviate и платный ключ OpenAI/Azure |
| 15 | DAG с callback при сбое (DAG и task), executor у task | ch15_callbacks_dag.py | ok: DagBag без ошибок, `airflow dags test -f ... nightly_export 2026-01-02` дал failed run и сработавший callback DAG (Airflow 3.4.0). После теста в логе шум sqlite (MissingGreenlet при закрытии соединения), на результат не влияет |
| 15 | Проверка без сервера: значения по умолчанию, DagBag, callbacks | ch15_check.py | ok (6 запусков `$VENV/bin/python -I`, вывод одинаков, Airflow 3.4.0) |
| 15 | Модель лимитов parallelism, max_active_tasks_per_dag, default_pool | ch15_limits.py | ok (6 запусков `python3 -I`, вывод одинаков) |
| 15 | Какие пакеты StatsD шлёт Airflow (свой UDP-сервер вместо exporter) | ch15_statsd.py | ok (6 запусков, вывод одинаков, Airflow 3.4.0, `statsd==4.0.1`). Использует внутренние модули Airflow 3.4, могут измениться |
| 15 | CeleryExecutor, KubernetesExecutor, EdgeExecutor, remote logging | (настройки в тексте страницы) | не запускали: нужны broker, кластер Kubernetes, облачное хранилище |
| 15 | statsd-exporter, Prometheus, Grafana, SMTP | (настройки в тексте страницы) | не запускали: нужны Docker и почтовый сервер |
| 16 | Fernet: шифрование, чужой ключ, FERNET_KEY_CMD, шифрование пароля connection | ch16_fernet.py | ok (6 запусков `$VENV/bin/python -I`, вывод одинаков; Airflow 3.4.0, cryptography 50.0.2) |
| 16 | Порядок поиска секрета: заглушка backend, env, нет нигде | ch16_secrets_backend.py, ch16_demo_backend.py | ok (6 запусков, вывод одинаков). Настоящий Vault не запускали: нужен сервер Vault и provider hashicorp |
| 16 | Self-signed certificate командой openssl (rsa:2048 вместо 4096 книги), SAN, настройки api.ssl_cert и api.ssl_key, auth_manager по умолчанию | ch16_tls_auth.py | ok (6 запусков, вывод одинаков; OpenSSL 3.6.4). UI по HTTPS не запускали: нужен сервер Airflow |
| 16 | DAG call_partner_api (HttpOperator, conn_id из backend) | ch16_partner_dag.py, ch16_check.py | только DagBag: ошибок нет. Запрос не запускали: нужен connection и API |
| 16 | RBAC, LDAP (webserver_config.py, FabAuthManager), `airflow users create` | нет скрипта | не запускали: нужен provider FAB и сервер LDAP |
| 17 | Слияние values chart и файла, как в helm (PyYAML 6.0.3) | ch17_values_layers.py | ok (6 запусков `python3 -I`, вывод одинаков). `helm upgrade` на кластере не запускали |
| 17 | DAG с двумя executors и `pod_override` | ch17_multi_executor_dag.py | DagBag без ошибок (Airflow 3.4.0, cncf-kubernetes 11.0.0, `[core] executor=CeleryExecutor,KubernetesExecutor`). `dags test` и запуск tasks не запускали: нужны Celery и Kubernetes |
| 17 | Проверка DAG через DagBag | ch17_check_executor_dag.py | ok (6 запусков, вывод одинаков) |
| 17 | values для git-sync | ch17_git_sync_values.yaml | YAML разбирается (PyYAML). На кластере не запускали: нужны Kubernetes и Git |
| 17 | Dockerfile, helm, kubectl, Astro, Composer, MWAA | нет | не запускали: нужны Docker registry, Kubernetes, облако |
