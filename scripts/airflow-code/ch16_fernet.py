"""Глава 16: шифрование секретов ключом Fernet. Без сервера.
Запуск: $VENV/bin/python -I scripts/airflow-code/ch16_fernet.py"""
import os
import tempfile
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

key = Fernet.generate_key()
print("длина ключа:", len(key.decode()), "символа")

token = Fernet(key).encrypt(b"topsecret")
print("в базе лежит:", "gAAAA..., длина", len(token), "| открытый текст виден:", b"topsecret" in token)
print("с тем же ключом:", Fernet(key).decrypt(token).decode())
try:
    Fernet(Fernet.generate_key()).decrypt(token)
except InvalidToken:
    print("с другим ключом: InvalidToken")

# Airflow: ключ из файла через FERNET_KEY_CMD, пароль connection шифруется сам
keyfile = Path(tempfile.mkdtemp()) / "fernet.key"
keyfile.write_text(key.decode())
keyfile.chmod(0o400)
os.environ["AIRFLOW__CORE__FERNET_KEY_CMD"] = f"cat {keyfile}"

from airflow.configuration import conf  # noqa: E402
from airflow.models.connection import Connection  # noqa: E402

print("Airflow читает ключ из файла:", conf.get("core", "fernet_key") == key.decode())
conn = Connection(conn_id="demo", conn_type="http", host="h", password="topsecret")
print("поле password в базе:", "зашифровано" if conn._password != "topsecret" else "открытый текст")
print("conn.password:", conn.password)
