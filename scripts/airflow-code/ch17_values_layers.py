"""Глава 17: как helm собирает настройки. Чистый Python + PyYAML 6.0.3, кластер не нужен.
Helm берёт значения chart по умолчанию и накладывает на них values-файл.
Прежние values-файлы он не помнит, поэтому каждый новый файл повторяет старые правки."""
import yaml

# Урезанные значения chart по умолчанию (настоящие даёт `helm show values`)
DEFAULTS = yaml.safe_load("""
postgresql: {enabled: true}
webserver: {defaultUser: {username: admin}}
apiSecretKeySecretName: null
""")

FILE_01_USER = "webserver: {defaultUser: {username: airflow}}"
FILE_02_SECRET = "apiSecretKeySecretName: my-apiserver-secret"
FILE_03_DB = "postgresql: {enabled: false}"


def merge(base, over):
    """Глубокое слияние: значения из over заменяют значения из base."""
    out = dict(base)
    for key, val in over.items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = merge(out[key], val)
        else:
            out[key] = val
    return out


def release(*files):
    """Итоговые настройки после `helm upgrade -f файл ...` (без --reuse-values)."""
    values = DEFAULTS
    for text in files:
        values = merge(values, yaml.safe_load(text))
    return values


def show(title, values):
    print(title)
    print("  встроенный PostgreSQL:", values["postgresql"]["enabled"])
    print("  пользователь:", values["webserver"]["defaultUser"]["username"])
    print("  secret key:", values["apiSecretKeySecretName"])


# Файл 03 накапливает правки 01 и 02, как в книге
cumulative = FILE_03_DB + "\n" + FILE_02_SECRET + "\n" + FILE_01_USER
show("Файл 03 повторяет прежние правки:", release(cumulative))
show("Файл 03 только с новой правкой:", release(FILE_03_DB))
