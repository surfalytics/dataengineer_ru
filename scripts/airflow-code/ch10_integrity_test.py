"""DAG integrity test: проверяет каждый файл в папке dags/.
Это тест для pytest. Запуск как скрипта показывает работу на трёх тестовых DAG."""
import contextlib
import os
import sys
import tempfile
from pathlib import Path

from airflow.models import DagBag


def check_file(dag_file):
    """Возвращает текст ошибки или None, если файл в порядке."""
    bag = DagBag(dag_folder=str(dag_file))
    if bag.import_errors:
        return "; ".join(msg.strip().splitlines()[-1] for msg in bag.import_errors.values())
    if not bag.dags:
        return "в файле нет DAG"
    return None


# pytest берёт файлы из папки dags/ рядом с tests/
try:
    import pytest
    DAG_FILES = sorted((Path(__file__).parent.parent / "dags").rglob("*.py"))

    @pytest.mark.parametrize("dag_file", DAG_FILES, ids=str)
    def test_dag_loads(dag_file):
        assert check_file(dag_file) is None
except ImportError:
    pass

@contextlib.contextmanager
def quiet():
    """Прячет вывод логов Airflow (на уровне файловых дескрипторов)."""
    sys.stdout.flush()
    saved = os.dup(1), os.dup(2)
    null = os.open(os.devnull, os.O_WRONLY)
    os.dup2(null, 1), os.dup2(null, 2)
    try:
        yield
    finally:
        os.dup2(saved[0], 1), os.dup2(saved[1], 2)
        for fd in (*saved, null):
            os.close(fd)


GOOD = '''
from airflow.sdk import DAG
from airflow.providers.standard.operators.empty import EmptyOperator
with DAG("good", schedule=None):
    EmptyOperator(task_id="a") >> EmptyOperator(task_id="b")
'''
CYCLE = '''
from airflow.sdk import DAG
from airflow.providers.standard.operators.empty import EmptyOperator
with DAG("cycle", schedule=None):
    t1, t2, t3 = (EmptyOperator(task_id=f"t{i}") for i in (1, 2, 3))
    t1 >> t2 >> t3 >> t1
'''
NO_COMMAND = '''
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator
with DAG("no_command", schedule=None):
    BashOperator(task_id="this_should_fail")
'''
HELPER = "def util():\n    return 1\n"

if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        for name, code in [("good.py", GOOD), ("cycle.py", CYCLE),
                           ("no_command.py", NO_COMMAND), ("helper.py", HELPER)]:
            path = Path(tmp) / name
            path.write_text(code)
            with quiet():
                result = check_file(path)  # DagBag пишет трассировки в лог, прячем их
            print(f"{name:14} -> {result or 'ok'}")
    sys.exit(0)
