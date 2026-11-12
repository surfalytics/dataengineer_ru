---
title: "DuckDB: Up and Running, глава 9: DuckDB в облаке с MotherDuck"
head:
  - tag: title
    content: "MotherDuck: DuckDB в облаке и hybrid-запросы | Инжиниринг Данных"
description: "Конспект главы 9 DuckDB: Up and Running на русском. MotherDuck, базы и схемы, shares, AI-функции prompt_sql, подключение через CLI и hybrid-запросы."
sidebar:
  order: 9
  label: "9. MotherDuck"
tags:
  - books
  - duckdb
  - motherduck
  - cloud
---

**Главная мысль:** MotherDuck — это DuckDB как облачный сервис. Вы загружаете данные один раз, делитесь ими по ссылке и запускаете запросы без своего сервера. Особенность — hybrid-запрос: один запрос читает и локальные файлы, и таблицы в облаке.

## Что такое MotherDuck

- Serverless-платформа аналитики на базе DuckDB. Без установки и настройки машины.
- Читает Parquet, CSV, JSON, Iceberg и Delta Lake.
- Каждому пользователю даётся свой изолированный compute. Он масштабируется независимо.
- Функция Dual Execution: часть запроса идёт локально, часть в облаке.
- Инфраструктура работает в AWS. Сервисы идут в контейнерах под Kubernetes.

### Тарифы

| План | Цена в книге | Что входит |
|---|---|---|
| Trial | 30 дней бесплатно | Все возможности |
| Free | $0 в месяц на организацию | 5 участников, 10 CU-часов, 10 GB хранилища |
| Standard | $25 в месяц на организацию | Безлимит участников, 100 CU-часов, 100 GB. Можно докупать |

`CU` — compute unit, единица вычислений. Цены и лимиты быстро меняются. Проверьте их на сайте перед выбором. Это данные на момент выхода книги (декабрь 2024).

## Первый вход

Вход через Google, GitHub или email с паролем. Веб-интерфейс похож на Jupyter: слева панели, справа ноутбук с SQL-ячейками.

Слева два раздела:

- **Notebooks** — ваши ноутбуки.
- **Attached databases** — подключённые базы.

По умолчанию подключены две базы:

| База | Что это | Права |
|---|---|---|
| `my_db` | Ваша база для своих данных | Чтение и запись |
| `sample_data` | Учебные таблицы | Только чтение (shared database) |

## Иерархия объектов

Порядок имён: `база.схема.таблица`. Пример: `my_db.main.airlines`.

- В базе есть схемы. Схема по умолчанию — `main`.
- Схема группирует связанные таблицы.
- Загрузка данных: кнопка Add Data, затем в ячейке указать полное имя таблицы: `CREATE OR REPLACE TABLE my_db.main.airlines AS SELECT * FROM read_csv_auto(['airlines.csv'])`.
- `CREATE SCHEMA my_db.titanic` создаёт схему.
- `DROP SCHEMA titanic CASCADE` удаляет схему вместе с таблицами. Без `CASCADE` непустую схему не удалить.

## Базы: создать, выбрать, отключить

```text
CREATE DATABASE flights_db;
USE flights_db;
DETACH flights_db;
```

- Новую базу можно создать только командой SQL. Через интерфейс пока нельзя.
- `USE` выбирает базу по умолчанию для следующих запросов.
- `DETACH` отключает базу и освобождает ресурсы. Данные остаются. Потом её можно подключить снова.

## Shares: общий доступ без копий

Share даёт другим людям доступ к вашей базе только для чтения. Данные не копируются.

| Шаг | Команда или действие |
|---|---|
| Создать share | В меню базы выбрать Share, задать имя и доступ |
| Уровни доступа | Anyone in my organization или Anyone with the share link |
| Подключить чужой share | `ATTACH 'md:_share/<имя>/<id>' AS my_alias;` |
| Показать свои shares | `LIST SHARES` |
| Передать новые изменения | `UPDATE SHARE <имя>;` |
| Остановить | Drop в меню share |

- Share — это снимок базы. Получатели видят изменения только после `UPDATE SHARE`.
- Получатель задаёт своё имя базы через `AS`. Иначе имя может совпасть с его `my_db`.
- Ссылку с доступом «anyone with the link» нельзя выкладывать публично, если данные закрытые.

## Работа с данными в интерфейсе

- Результат запроса показывается вместе со статистикой по колонкам справа.
- Для текста видно частоты значений. Для чисел — гистограмма и квантили: min, медиана, mean, стандартное отклонение.
- Это быстрая EDA без отдельных запросов `GROUP BY`.

## AI-функции

MotherDuck встроил LLM в SQL. Это функции и pragma.

| Что | Что делает |
|---|---|
| `prompt_sql()` | Пишет SQL по вопросу на английском |
| `prompt_query` | Сразу даёт ответ на вопрос о данных |
| `prompt_fixup()` | Исправляет запрос |
| `prompt_fix_line()` | Исправляет запрос построчно |
| `prompt_schema()` | Описывает содержимое базы |
| `prompt_explain()` | Объясняет, что делает запрос |

Пример из книги (не запускайте без аккаунта):

```text
USE my_db;
CALL prompt_sql('How many passengers travelled alone and survived?');
PRAGMA prompt_query('How many airlines are there?');
```

`prompt_sql` возвращает текст запроса. Вы читаете его и запускаете сами. `prompt_query` сразу отдаёт результат.

> Проверяйте SQL от LLM перед запуском. Модель может понять вопрос неверно. Например, «один пассажир» она может записать как условие на несколько колонок.

## MotherDuck через DuckDB CLI

Нужен DuckDB версии 1.0.0 или выше.

```text
duckdb
ATTACH 'md:';
```

- Команда выдаёт код. Откройте ссылку, проверьте, что код тот же, подтвердите вход и дайте доступ.
- После входа токен сохраняется. `PRAGMA PRINT_MD_TOKEN;` показывает его. Его можно положить в переменную окружения, чтобы не входить снова.
- Токен — это пароль. Не публикуйте его и не коммитьте.
- `SHOW databases;`, `SELECT current_database();`, `SELECT current_schema();` показывают, где вы.
- Дальше всё работает как локально: `USE my_db.titanic;`, `CREATE DATABASE`, `INSERT`.

## Hybrid-запросы

Один запрос соединяет локальный файл и облачную таблицу.

```text
SELECT f.AIRLINE, f.FLIGHT_NUMBER, a.AIRLINE AS airline_name
FROM (SELECT AIRLINE, FLIGHT_NUMBER FROM './flights.csv' LIMIT 10) AS f
JOIN my_db.main.airlines AS a
  ON f.AIRLINE = a.IATA_CODE;
```

- Большой файл остаётся у вас. Небольшой справочник лежит в облаке.
- Обработка делится между локальной машиной и облаком (Dual Execution). Передаётся только нужное.

## Ключевые термины

| Термин | Значение |
|---|---|
| MotherDuck | Облачный сервис на DuckDB |
| Serverless | Нет своего сервера. Платите за использование |
| Compute unit (CU) | Единица вычислений в тарифе |
| Share | Доступ к снимку базы только для чтения |
| `ATTACH` / `DETACH` | Подключить / отключить базу |
| Schema | Группа таблиц внутри базы |
| Dual Execution | Запрос идёт частично локально, частично в облаке |
| Hybrid query | Запрос по локальным и облачным данным |

## Что это значит на практике

- Для небольшой команды MotherDuck — простое хранилище без администрирования. Для больших нагрузок проверьте тарифы и лимиты.
- Shares удобны для общих справочников и учебных данных. Не нужно копировать и рассылать файлы.
- Работайте в двух средах: локально для разработки, в облаке для общих данных. Hybrid-запрос соединяет их.
- LLM-функции ускоряют черновики SQL, но результат нужно проверять. В `dbt` такой SQL попадает в модели только после ревью и тестов.
- Токены MotherDuck храните как секреты, не в репозитории.

## Практика в DuckDB

Запустите `duckdb` в терминале. Блоки идут по порядку. Аккаунт не нужен. Вторая база в памяти играет роль облака: у неё те же команды `ATTACH`, `USE`, `CREATE SCHEMA`. Для настоящего облака адрес будет `md:` вместо `:memory:`.

### Шаг 1. «Облачная» база и таблицы

```sql
-- вторая база. В MotherDuck было бы ATTACH 'md:my_db'
ATTACH ':memory:' AS cloud_db;

CREATE SCHEMA cloud_db.ref;

CREATE TABLE cloud_db.ref.airlines AS
SELECT * FROM (VALUES
    ('AA', 'Air Alpha'),
    ('BB', 'Blue Bird'),
    ('CC', 'Cloud Carrier')
) t(iata_code, airline_name);

-- «локальные» рейсы в основной базе
CREATE TABLE flights AS
SELECT
    ['AA', 'BB', 'CC', 'DD'][1 + i % 4] AS airline,
    1000 + i AS flight_number
FROM range(0, 12) t(i);
```

### Шаг 2. Проверяем

```sql
SHOW DATABASES;
SELECT current_database() AS db, current_schema() AS schema_name;
SELECT count(*) AS n FROM cloud_db.ref.airlines;  -- ожидаем 3
```

### Шаг 3. Hybrid-запрос

```sql
SELECT f.airline, a.airline_name, count(*) AS flights
FROM flights AS f
LEFT JOIN cloud_db.ref.airlines AS a ON f.airline = a.iata_code
GROUP BY f.airline, a.airline_name
ORDER BY f.airline;
```

Проверка: для авиакомпании `DD` имени нет. Это `NULL`, потому что в справочнике её нет.

### Задания

1. Выберите `cloud_db.ref` как схему по умолчанию командой `USE` и прочитайте `airlines` без полного имени.
2. Создайте базу `scratch`, таблицу в ней, потом отключите базу командой `DETACH`.
3. Найдите рейсы, у которых нет авиакомпании в справочнике.
4. Удалите схему `ref` вместе с таблицами.

<details>
<summary>Решение</summary>

```sql
-- 1. короткое имя после USE
USE cloud_db.ref;
SELECT count(*) AS n FROM airlines;
USE memory.main;

-- 2. своя база и DETACH
ATTACH ':memory:' AS scratch;
CREATE TABLE scratch.main.t AS SELECT 1 AS id;
DETACH scratch;

-- 3. рейсы без записи в справочнике (антиджойн)
SELECT f.*
FROM flights AS f
LEFT JOIN cloud_db.ref.airlines AS a ON f.airline = a.iata_code
WHERE a.iata_code IS NULL;

-- 4. схема удаляется только с CASCADE, если в ней есть таблицы
DROP SCHEMA cloud_db.ref CASCADE;
SELECT count(*) AS schemas_left FROM information_schema.schemata WHERE catalog_name = 'cloud_db' AND schema_name = 'ref';
```

Пункт 3 вернул 3 рейса компании `DD`. Последний запрос вернул 0: схемы больше нет.

</details>

## Вопросы для самопроверки

1. Чем MotherDuck отличается от локального DuckDB? Что он добавляет?
2. Что такое share и почему получатель не может менять данные?
3. Как получить свежие изменения в share после правки базы?
4. Что такое hybrid-запрос? Приведите пример, где он удобен.

Предыдущая: [Глава 8. Удалённые данные](/book-summaries/engineering/duckdb-up-and-running/08-remote-data/). Следующей главы нет. Вернитесь к [обзору книги](/book-summaries/engineering/duckdb-up-and-running/).
