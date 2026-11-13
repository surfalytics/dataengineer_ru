"""Глава 16: порядок поиска секрета. Заглушка DemoBackend (ch16_demo_backend.py) играет роль Vault.
Запуск: $VENV/bin/python -I scripts/airflow-code/ch16_secrets_backend.py"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ["AIRFLOW__CORE__FERNET_KEY"] = "YlCImzjge_TeZc7jPJ7Jz2pgOtb4yTssA1pVyqIADWg="  # только для демо
os.environ["AIRFLOW__SECRETS__BACKEND"] = "ch16_demo_backend.DemoBackend"
os.environ["AIRFLOW_CONN_BOTH"] = "http://env-host:1?token=env-token"
os.environ["AIRFLOW_CONN_ONLY_ENV"] = "http://env-host:1?token=env-token"

from airflow.models.connection import Connection  # noqa: E402

print("secure_api: только в backend; both: и в backend, и в env; only_env: только в env")
for conn_id in ["secure_api", "both", "only_env", "nowhere"]:
    try:
        print(f"{conn_id:11} -> {Connection.get_connection_from_secrets(conn_id).host}")
    except Exception as e:
        print(f"{conn_id:11} -> {type(e).__name__}")
