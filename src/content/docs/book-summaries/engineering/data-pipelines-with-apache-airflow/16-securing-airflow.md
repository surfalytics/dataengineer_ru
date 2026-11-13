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

## О чём глава

Предыдущая [глава 15](/book-summaries/engineering/data-pipelines-with-apache-airflow/15-operating-in-production/) учила запускать Airflow в production. Эта отвечает на вопрос: как закрыть его от чужих. Пять тем:

- роли пользователей в UI (RBAC);
- шифрование секретов в базе ключом Fernet;
- вход через LDAP;
- шифрование трафика (HTTPS);
- secrets backend, например HashiCorp Vault.

![Слои защиты Airflow: HTTPS, RBAC, LDAP, Fernet и secrets backend](/assets/data-pipelines-with-apache-airflow/ch16-security-layers.png)

## Роли в UI (RBAC)

Откройте `http://localhost:8080`. Airflow просит логин и пароль. Это интерфейс RBAC (role-based access control).

В модели RBAC у каждого пользователя ровно одна роль. Роль состоит из прав (permissions). Право разрешает операцию над частью UI. Пример: `can edit on ConnectionModelView` разрешает менять connections.

Пользователя создают командой. Без флага `--password` Airflow спросит пароль:

```bash
airflow users create --role Admin --username bobsmith \
  --email bobsmith@company.com --firstname Bob --lastname Smith
```

Есть пять ролей по умолчанию.

| Роль | Для кого | Что может |
|---|---|---|
| Admin | Тот, кто управляет безопасностью | Всё, включая security view |
| Public | Неавторизованные | Ничего |
| Viewer | Только чтение | Видит DAG |
| User | Разработчик без доступа к секретам | Как Viewer, плюс clear, trigger, pause |
| Op | Разработчик DAG | Как User, плюс connections, pools, variables, XCom, config |

- Права очень мелкие: у каждого пункта меню своё. Нужное право проще найти в других ролях.
- `Admin` в production давайте с осторожностью.

RBAC построен на Flask-AppBuilder (FAB). Настройки лежат в `webserver_config.py` в `$AIRFLOW_HOME`. Если файла нет, Airflow создаст его сам. В нём и безопасность, и мелочи, например тема `APP_THEME`.

> **Пояснение:** В Airflow 3 FAB вынесен в отдельный provider. По умолчанию работает `SimpleAuthManager` (проверили в Airflow 3.4.0). Чтобы получить роли и LDAP из книги, поставьте provider FAB и включите `FabAuthManager`.

## Шифрование данных в базе

Сначала сократите attack surface: откройте наружу как можно меньше. Каждый открытый компонент это путь для чужого. Если UI нужен снаружи, не делайте его публичным: в облаке не давайте внешний IP или пускайте только свой диапазон адресов.

Затем защитите данные на случай взлома. Без шифрования пароли и connections лежат в базе открытым текстом. Любой, кто читает базу, их видит. Включите шифрование до создания первых пользователей и connections.

Airflow шифрует секреты ключом Fernet. Это symmetric encryption: один ключ и шифрует, и расшифровывает.

- Ключ задаёт `AIRFLOW__CORE__FERNET_KEY`.
- Он защищает connections, variables и пароли пользователей.
- Потеряли ключ, и секреты не расшифровать. Украли ключ, и секреты прочитают.
- Чтобы не держать ключ в переменной открытым текстом, задайте `AIRFLOW__CORE__FERNET_KEY_CMD=cat /path/to/secret`. Файл с ключом открывайте только нужным пользователям или группам.

## Вход через LDAP

Большинство компаний уже имеет каталог пользователей. Airflow может проверять логин в нём. Пользователь создаётся один раз для всех приложений.

Directory service хранит сведения о людях, устройствах и сервисах. Примеры: Microsoft Entra ID, OpenLDAP. LDAP (Lightweight Directory Access Protocol) это протокол запросов к нему. Связь такая же, как у SQL и базы данных. Но цель другая: база нужна для транзакций, каталог для частого чтения редко меняющихся данных, например учётных записей.

Данные в каталоге образуют дерево DIT (directory information tree). Каждый узел это entry: набор пар атрибут-значение. Уникальное имя записи это DN (distinguished name). Сокращения в DN: `dc` domain component (домен делят по точкам), `ou` organizational unit, `cn` common name.

![Дерево каталога LDAP и DN записи Боба](/assets/data-pipelines-with-apache-airflow/ch16-ldap-dit.png)

У LDAP свои операции, как у SQL свои команды. Для входа хватает трёх:

| Операция | Что делает |
|---|---|
| bind | Входит в каталог под нужным пользователем. Первое соединение анонимное |
| search | Ищет записи по фильтру, например `uid=bsmith` |
| unbind | Закрывает соединение |

Включите FAB: `AIRFLOW__CORE__AUTH_MANAGER` равен `airflow.providers.fab.auth_manager.fab_auth_manager.FabAuthManager`. Затем настройте `webserver_config.py`:

- `AUTH_TYPE = AUTH_LDAP`;
- `AUTH_LDAP_SERVER`, `AUTH_LDAP_SEARCH`: адрес и ветка поиска;
- `AUTH_LDAP_BIND_USER`, `AUTH_LDAP_BIND_PASSWORD`: сервисный пользователь;
- `AUTH_LDAP_UID_FIELD`: поле с логином;
- `AUTH_USER_REGISTRATION = True` и `AUTH_USER_REGISTRATION_ROLE`: роль по умолчанию для каждого, кто вошёл.

Книга предупреждает: переноса LDAP-групп в роли RBAC нет. Роль можно поменять вручную в таблице `ab_user_role` в metastore.

## Шифрование трафика (HTTPS)

Данные могут утечь и в пути. При атаке man-in-the-middle (MITM) чужой стоит между браузером и сервером, читает сообщения и пересылает их дальше. Заметить это трудно. Но можно сделать перехваченные данные бесполезными: зашифровать их.

HTTP не проверяет собеседника и передаёт всё открытым текстом. HTTPS использует TLS. TLS сочетает два вида шифрования.

| Вид | Ключи | Как работает |
|---|---|---|
| Symmetric | Один | Один ключ шифрует и расшифровывает. Потеря ключа открывает всё |
| Asymmetric | Public и private | Зашифровано public, расшифровать можно только private. Public можно раздавать |

![Рукопожатие HTTPS: certificate, session key и шифрование трафика](/assets/data-pipelines-with-apache-airflow/ch16-https-handshake.png)

Certificate это файл с public key. Private key знает только сервер. Поэтому никому не передавайте его: кто его имеет, расшифрует трафик.

Для Airflow нужны private key и certificate. Их выдаёт certificate authority, либо вы делаете self-signed certificate командой `openssl req -x509`. Современные браузеры требуют в нём расширение SAN (subjectAltName), например `DNS:localhost,IP:127.0.0.1`. Пути к файлам задают `AIRFLOW__API__SSL_CERT` и `AIRFLOW__API__SSL_KEY`. Они относятся к api-server, публичной точке Airflow. После запуска UI доступен по `https://localhost:8080`.

Браузер сначала предупредит о self-signed certificate. У системы есть список доверенных центров, и вашего в нём нет. Нужно добавить certificate в доверенные вручную. Для общего адреса так делать неудобно. Возьмите certificate у доверенного центра, например Let's Encrypt.

## Secrets backend

Многие компании держат секреты в одной системе: HashiCorp Vault, Azure Key Vault, AWS SSM, Google Cloud Secret Manager. Там есть ротация и версии, которых в Airflow нет. Secrets backend даёт Airflow брать connections и variables оттуда. В коде DAG ничего не меняется.

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

Здесь нет слова Vault. Оператор знает только `conn_id`. Раньше URL лежал бы в connection Airflow, теперь он может лежать в Vault. Условия для Vault backend:

- он включается через `AIRFLOW__SECRETS__BACKEND` (класс) и `AIRFLOW__SECRETS__BACKEND_KWARGS` (адрес, токен, `connections_path`);
- у всех секретов общий prefix (по умолчанию `secret`);
- connection лежит в ключе `conn_uri`, variable в ключе `value`;
- имя секрета это путь: `secret/connections/partner_api`.

Connection записывают как URI, например `http://secure_api:5000?token=supersecret`. Классы backend: `VaultBackend` (HashiCorp), `SecretsManagerBackend` (AWS), `CloudSecretManagerBackend` (Google), `AzureKeyVaultBackend` (Azure). Их `BACKEND_KWARGS` ищите в документации provider.

![Порядок поиска секрета: secrets backend, переменные среды, metastore](/assets/data-pipelines-with-apache-airflow/ch16-secrets-lookup.png)

Backend не заменяет другие места, а добавляет ещё одно. Порядок поиска: secrets backend, переменные среды (`AIRFLOW_CONN_*`, `AIRFLOW_VAR_*`), metastore. Секрет хранится в одном месте, поэтому риск утечки ниже.

## Итоги главы

- Безопасность это несколько уровней. Цель: уменьшить attack surface.
- RBAC даёт каждому пользователю одну роль с набором мелких прав.
- LDAP убирает отдельное управление пользователями в Airflow.
- Fernet key делает пароли в metastore нечитаемыми. Ключ нельзя терять и нельзя открывать.
- HTTPS (TLS) делает перехваченный трафик бесполезным для атакующего.
- Secrets backend хранит секреты в одной системе. Порядок поиска: backend, env, metastore.
- Обновляйте Airflow: в релизах есть security-патчи.

## Ключевые термины

| Термин | Значение |
|---|---|
| RBAC | Доступ по ролям: пользователь, роль, права |
| Attack surface | Число точек, через которые можно атаковать |
| Fernet key | Ключ для шифрования секретов в metastore |
| Symmetric encryption | Один ключ на шифрование и расшифровку |
| Asymmetric encryption | Пара ключей: public и private |
| LDAP | Протокол запросов к каталогу пользователей |
| DIT / DN | Дерево каталога и уникальное имя записи |
| MITM | Атака, при которой чужой читает трафик между двумя сторонами |
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

## Практика

Скрипты работают без запущенного Airflow (3.4.0). Подробности в [README.md](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/README.md).

**Fernet.** Шифруем, пробуем чужой ключ, затем Airflow берёт ключ из файла. Скрипт: [ch16_fernet.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch16_fernet.py).

```text
длина ключа: 44 символа
в базе лежит: gAAAA..., длина 100 | открытый текст виден: False
с тем же ключом: topsecret
с другим ключом: InvalidToken
Airflow читает ключ из файла: True
поле password в базе: зашифровано
conn.password: topsecret
```

**Порядок поиска секрета.** Заглушка `DemoBackend` вместо Vault знает `secure_api` и `both`, переменные среды знают `both` и `only_env`. Скрипт: [ch16_secrets_backend.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch16_secrets_backend.py).

```text
secure_api: только в backend; both: и в backend, и в env; only_env: только в env
secure_api  -> vault-host
both        -> vault-host
only_env    -> env-host
nowhere     -> AirflowNotFoundException
```

**Certificate и настройки.** Команда `openssl` делает self-signed certificate. DAG из примера разбирается без ошибок. Скрипты: [ch16_tls_auth.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch16_tls_auth.py) и [ch16_check.py](https://github.com/surfalytics/dataengineer.ru/tree/main/scripts/airflow-code/ch16_check.py).

```text
subject: CN=localhost
SAN: ['localhost', '127.0.0.1']
срок, дней: 365
самоподписанный: True
private key в отдельном файле: True
api.ssl_cert задан: True
api.ssl_key задан: True
auth_manager по умолчанию: SimpleAuthManager
```

```text
ошибки разбора: нет
conn_id в DAG: partner_api
```

Не запускали: RBAC и LDAP (нужен provider FAB и каталог), настоящий Vault (нужен сервер), запуск UI по HTTPS (нужен сервер Airflow). Эти части описаны по книге.

### Задания

**1. Смените ключ.** Что увидит Airflow, если после шифрования connections заменить `FERNET_KEY` на новый?

<details>
<summary>Решение</summary>

Расшифровка не удастся: вывод выше показывает `InvalidToken` для чужого ключа. Поэтому ключ нужно хранить и делать backup. Проверено запуском.

</details>

**2. Где лежит `both`?** Что вернёт поиск, если `both` есть и в backend, и в переменной среды? А что, если секрета нет нигде?

<details>
<summary>Решение</summary>

Вернётся значение из backend: хост `vault-host`. Если секрета нет нигде, будет `AirflowNotFoundException`. Проверено запуском.

</details>

**3. Какую роль выдать?** Аналитик должен запускать и ставить на паузу DAG, но не видеть connections. Дежурный инженер должен ещё менять variables и pools. Какие роли им дать?

<details>
<summary>Решение</summary>

Аналитику `User`: у неё есть clear, trigger, pause, но нет доступа к секретам. Инженеру `Op`: она добавляет connections, pools и variables. Не запускали: ответ по таблице ролей книги.

</details>

## Вопросы для самопроверки

1. Чем отличаются роли `User` и `Op`? Кому вы дадите `Admin`?
2. Что будет с connections в metastore, если потерять Fernet key?
3. Почему при HTTPS перехваченный трафик бесполезен для атакующего?
4. В каком порядке Airflow ищет connection, если включён secrets backend?

Предыдущая: [Эксплуатация Airflow в production](/book-summaries/engineering/data-pipelines-with-apache-airflow/15-operating-in-production/). Следующая: [Варианты развёртывания Airflow](/book-summaries/engineering/data-pipelines-with-apache-airflow/17-deployment-options/).
