"""Глава 7: условие для PythonSensor. Обычный Python, Airflow не нужен."""
from pathlib import Path


def batch_is_ready(folder):
    """True, если есть хотя бы один файл данных и есть маркер конца загрузки."""
    path = Path(folder)
    has_data = any(path.glob("part-*.csv"))
    return has_data and (path / "_DONE").exists()
