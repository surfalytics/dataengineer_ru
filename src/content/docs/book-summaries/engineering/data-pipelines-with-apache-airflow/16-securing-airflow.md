---
title: "Data Pipelines with Apache Airflow, глава 16: Безопасность Airflow"
head:
  - tag: title
    content: "Безопасность Airflow: RBAC, Fernet, TLS, Vault | Инжиниринг Данных"
description: "Конспект главы 16 Data Pipelines with Apache Airflow на русском. RBAC, LDAP, Fernet key, HTTPS, secrets backend и HashiCorp Vault."
sidebar:
  order: 16
  label: "16. Безопасность"
tags:
  - books
  - airflow
  - security
---

**Главная мысль:** Airflow имеет доступ ко многим системам, поэтому это цель для атаки. Защита не одна кнопка. Нужно несколько слоёв: роли, шифрование секретов, шифрование трафика и внешнее хранилище секретов.

![Слои защиты Airflow: HTTPS, RBAC, LDAP, Fernet и secrets backend](/assets/data-pipelines-with-apache-airflow/ch16-security-layers.png)

## Роли в UI (RBAC)

В модели RBAC у пользователя одна роль. Роль состоит из прав. Право (permission) задаёт операцию над частью UI, например "можно редактировать Connections".

| Роль | Для кого | Что может |
|---|---|---|
| Admin | Тот, кто управляет безопасностью | Всё, включая security view |
| Public | Неавторизованные | Ничего |
| Viewer | Только чтение | Видит DAG |
| User | Разработчик без доступа к секретам | Как Viewer, плюс clear, trigger, pause |
| Op | Разработчик DAG | Как User, плюс connections, pools, variables, XCom, config |

- Права очень мелкие. Каждый пункт меню имеет своё право.
- Не давайте `Admin` без нужды. Это правило для production.
- Пользователя можно создать командой `airflow users create` с флагами роли, имени и email. Без `--password` Airflow спросит пароль.
- RBAC в книге построен на Flask-AppBuilder (FAB). Его настройки лежат в `webserver_config.py` в `$AIRFLOW_HOME`. Там же можно сменить тему.

## Шифрование данных в базе

Сначала сократите attack surface. Откройте наружу как можно меньше сервисов. UI не должен быть доступен всему интернету. В облаке не давайте внешний IP и разрешайте только свой диапазон адресов.

Затем защитите данные на случай взлома. Без шифрования пароли и connections лежат в базе открытым текстом. Любой, кто читает базу, их увидит.

- Airflow шифрует секреты ключом Fernet. Это симметричное шифрование: один ключ и для шифрования, и для расшифровки.
- Ключ задаёт параметр `AIRFLOW__CORE__FERNET_KEY`.
- Он защищает connections, variables и пароли пользователей.
- Потеряете ключ, и секреты не расшифровать. Кто украл ключ, тот их прочитает.
- Не храните ключ в переменной открытым текстом. Используйте `AIRFLOW__CORE__FERNET_KEY_CMD`: команда читает ключ из файла, а на файл ставят права только для нужных пользователей.
- Включайте шифрование до создания первых пользователей и connections.

## Вход через LDAP

Большинство компаний уже имеют каталог пользователей. Зачем заводить ещё одни пароли? Airflow может проверять логин в LDAP.

| Понятие | Смысл |
|---|---|
| Directory service | Хранилище для чтения: люди, устройства. Примеры: Entra ID, OpenLDAP |
| LDAP | Протокол запросов к нему. Как SQL для базы |
| DIT | Дерево каталога |
| Entry | Запись: набор атрибутов |
| DN | Уникальное имя записи |
| `dc`, `ou`, `cn` | Domain component, organizational unit, common name |

- Для входа нужны три операции: bind (войти под сервисным пользователем), search (найти пользователя) и unbind.
- Работает это через FAB. Включите `FabAuthManager` в `AIRFLOW__CORE__AUTH_MANAGER`. Затем настройте `webserver_config.py`: `AUTH_TYPE = AUTH_LDAP`, адрес сервера, ветку поиска, сервисного пользователя и поле логина.
- Автоматическая регистрация даёт всем вошедшим одну роль по умолчанию.
- Книга отмечает: переноса LDAP-групп в роли RBAC нет. Роль можно поменять вручную в таблице `ab_user_role`.

## Шифрование трафика (HTTPS)

HTTP передаёт всё открытым текстом. Атака man-in-the-middle читает пароли в пути. HTTPS использует TLS. TLS сочетает два вида шифрования.

| Вид | Ключи | Как работает |
|---|---|---|
| Symmetric | Один | Один ключ шифрует и расшифровывает |
| Asymmetric | Public и private | Зашифровано public, расшифровать можно только private |

Рукопожатие HTTPS в простых словах:

1. Браузер просит страницу.
2. Сервер отдаёт certificate с public key.
3. Браузер проверяет certificate.
4. Браузер шлёт случайный session key, зашифрованный public key.
5. Сервер расшифровывает его private key. Дальше обе стороны шифруют трафик session key.

Что нужно Airflow: private key (секретный) и certificate (можно показывать). Их выдаёт certificate authority или вы создаёте self-signed certificate командой `openssl`. Пути задают `AIRFLOW__API__SSL_CERT` и `AIRFLOW__API__SSL_KEY`. После этого UI доступен по `https://localhost:8080`.

- Self-signed certificate браузер не доверяет. Его нужно добавить в доверенные вручную.
- Для общего доступа берите certificate от доверенного центра, например Let's Encrypt.
- Private key не передавайте никому.

## Secrets backend

Компании часто держат секреты в одной системе: HashiCorp Vault, Azure Key Vault, AWS SSM, Google Secret Manager. У них есть ротация и версии, которых нет в Airflow. Secrets backend позволяет Airflow брать connections и variables оттуда.

![Порядок поиска секрета: secrets backend, переменные среды, metastore](/assets/data-pipelines-with-apache-airflow/ch16-secrets-lookup.png)

- В коде DAG ничего не меняется. Оператор указывает `conn_id`, а Airflow сам ищет секрет.
- Настройка: `AIRFLOW__SECRETS__BACKEND` (класс) и `AIRFLOW__SECRETS__BACKEND_KWARGS` (адрес, токен, prefix).
- У Vault backend свои правила: общий prefix, connection лежит в ключе `conn_uri`, variable в ключе `value`.
- Connection записывают в формате URI, например `http://host:5000?token=...`.
- Backend не заменяет другие места. Порядок поиска такой: secrets backend, переменные среды, metastore.

В конце глава советует обновлять Airflow. В новых версиях закрывают уязвимости.

## Пример кода

Проверено на Airflow 3.4: DAG загружается, генерация ключа Fernet работает. Для запуска нужен connection `partner_api`.

DAG не знает о Vault. Он ссылается только на `conn_id`.

```python
import pendulum
from airflow.providers.http.operators.http import HttpOperator
from airflow.sdk import DAG

with DAG(
    dag_id="call_partner_api",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    schedule=None,
):
    ping = HttpOperator(
        task_id="ping",
        http_conn_id="partner_api",  # секрет лежит в backend
        method="GET",
        endpoint="health",
    )
```

Ключ Fernet можно создать так:

```python
from cryptography.fernet import Fernet

print(Fernet.generate_key().decode())
```

## Ключевые термины

| Термин | Значение |
|---|---|
| RBAC | Доступ по ролям: пользователь, роль, права |
| Attack surface | Число точек, через которые можно атаковать |
| Fernet key | Ключ для шифрования секретов в metastore |
| Symmetric encryption | Один ключ на шифрование и расшифровку |
| Asymmetric encryption | Пара ключей: public и private |
| LDAP | Протокол запросов к каталогу пользователей |
| DN | Уникальное имя записи в каталоге |
| TLS / HTTPS | Шифрование трафика между браузером и сервером |
| Self-signed certificate | Certificate без подписи официального центра |
| Secrets backend | Внешнее хранилище секретов для connections и variables |

## Что это значит на практике

- Задайте `FERNET_KEY` до первого connection. Храните ключ вне репозитория и делайте его backup.
- Не выдавайте `Admin` разработчикам. Для них хватает `User` или `Op`.
- Подключите LDAP или SSO компании. Тогда увольнение сотрудника закрывает и доступ к Airflow.
- Не открывайте UI в интернет. Включите HTTPS, а на границе поставьте reverse proxy или load balancer с настоящим certificate.
- Держите пароли к `dbt`, warehouse и API в Vault или в Secret Manager. Тогда один секрет живёт в одном месте.
- Следите за релизами Airflow и ставьте security-патчи.

## Вопросы для самопроверки

1. Чем отличаются роли `User` и `Op`? Кому вы дадите `Admin`?
2. Что будет с connections в metastore, если потерять Fernet key?
3. Почему при HTTPS перехваченный трафик бесполезен для атакующего?
4. В каком порядке Airflow ищет connection, если включён secrets backend?

Предыдущая: [Эксплуатация Airflow в production](/book-summaries/engineering/data-pipelines-with-apache-airflow/15-operating-in-production/). Следующая: [Варианты развёртывания Airflow](/book-summaries/engineering/data-pipelines-with-apache-airflow/17-deployment-options/).
