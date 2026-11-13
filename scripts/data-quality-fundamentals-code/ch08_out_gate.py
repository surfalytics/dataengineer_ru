"""Глава 8: вывод SQL-блока 5 страницы (см. ch08_sqlrun.py)."""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).with_name("ch08_sqlrun.py")), init_globals={"BLOCK": 5})
