"""Заглушка вместо Vault: класс отдаёт connection строкой URI из словаря. Используется в ch16_secrets_backend.py."""
from airflow.secrets import BaseSecretsBackend


class DemoBackend(BaseSecretsBackend):
    DATA = {
        "secure_api": "http://vault-host:5000?token=vault-token",
        "both": "http://vault-host:5000?token=vault-token",
    }

    def get_conn_value(self, conn_id, team_name=None):
        return self.DATA.get(conn_id)

    def get_variable(self, key, team_name=None):
        return None
