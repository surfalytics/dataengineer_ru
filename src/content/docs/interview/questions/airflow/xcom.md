---
title: "XCom"
prev: {"label":"Как забрать только новые данные и безопасно повторить загрузку?","link":"/interview/questions/airflow/idempotency/"}
next: {"label":"Как выбрать оператор для выполнения работы?","link":"/interview/questions/airflow/operators/"}
editUrl: false
---

**XCom (cross-communication)** позволяет одной задаче передать другой небольшое сериализуемое значение. Например, выгрузка записала файл в объектное хранилище и вернула его URI, число строк и контрольную сумму. Следующая задача получает эти значения и открывает нужный файл.

XCom привязан к задаче, запуску и ключу. Возвращаемое значение многих операторов и функций `@task` автоматически попадает под ключ `return_value`. **Variable** хранит общее значение уровня установки и переживает отдельные запуски DAG.

## Можно ли передать DataFrame?

Стандартный backend хранит XCom в metadata DB. Большие результаты нагружают сериализацию, передачу и базу. Таблицу, DataFrame или большой JSON лучше положить в S3, файл или staging-таблицу и передать ссылку или идентификатор. **Универсального лимита в килобайтах для всех установок нет** — важны backend и настройки. Object Storage XCom Backend умеет выносить крупные значения за настраиваемый порог в объектное хранилище. [XCom](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/xcoms.html) · [Object Storage XCom Backend](https://airflow.apache.org/docs/apache-airflow-providers-common-io/stable/xcom_backend.html)
