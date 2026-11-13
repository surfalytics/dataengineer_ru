"""Глава 16: self-signed certificate командой openssl, настройки TLS и auth manager в Airflow. Без сервера.
Запуск: $VENV/bin/python -I scripts/airflow-code/ch16_tls_auth.py"""
import os
import subprocess
import tempfile
from pathlib import Path

from cryptography import x509
from cryptography.x509.oid import ExtensionOID

work = Path(tempfile.mkdtemp())
cmd = f"""openssl req -x509 -newkey rsa:2048 -sha256 -nodes -days 365 \
-keyout {work}/privatekey.pem -out {work}/certificate.pem -extensions san \
-config <(echo "[req]"; echo distinguished_name=req; echo "[san]"; echo subjectAltName=DNS:localhost,IP:127.0.0.1) \
-subj "/CN=localhost" 2>/dev/null"""
subprocess.run(["bash", "-c", cmd], check=True)

cert = x509.load_pem_x509_certificate((work / "certificate.pem").read_bytes())
san = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME).value
print("subject:", cert.subject.rfc4514_string())
print("SAN:", [str(v.value) for v in san])
print("срок, дней:", (cert.not_valid_after_utc - cert.not_valid_before_utc).days)
print("самоподписанный:", cert.issuer == cert.subject)
print("private key в отдельном файле:", (work / "privatekey.pem").exists())

os.environ["AIRFLOW__API__SSL_CERT"] = str(work / "certificate.pem")
os.environ["AIRFLOW__API__SSL_KEY"] = str(work / "privatekey.pem")
from airflow.configuration import conf  # noqa: E402

print("api.ssl_cert задан:", conf.get("api", "ssl_cert").endswith("certificate.pem"))
print("api.ssl_key задан:", conf.get("api", "ssl_key").endswith("privatekey.pem"))
print("auth_manager по умолчанию:", conf.get("core", "auth_manager").rsplit(".", 1)[-1])
