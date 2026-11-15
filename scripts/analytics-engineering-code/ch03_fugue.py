"""Глава 3: один запрос FugueSQL на разных движках (пример 3-73 книги).
Spark не нужен: показываем движки pandas и duckdb."""
import tempfile
import warnings
from pathlib import Path

import duckdb
warnings.filterwarnings("ignore", category=UserWarning)  # fugue-sql-antlr: pkg_resources
import fugue.api as fa  # noqa: E402
import pandas as pd

books = pd.DataFrame({
    "title": ["SQL для начинающих", "Python для анализа", "dbt на практике", "Основы Spark"],
    "author": ["Иванова", "Петров", "Иванова", "Козлов"],
    "units_sold": [1000, 800, 1200, 600],
})

with tempfile.TemporaryDirectory() as tmp:
    src = Path(tmp) / "books.parquet"
    out = Path(tmp) / "ivanova.parquet"
    books.to_parquet(src)

    # Один и тот же текст запроса. LOAD и PRINT — расширения FugueSQL
    query = f"""
    LOAD "{src}"
    SELECT author, COUNT(title) AS nb_books
    GROUP BY author
    ORDER BY author
    PRINT
    """
    fa.fugue_sql(query, engine="pandas")
    fa.fugue_sql(query, engine="duckdb")   # в книге здесь ещё engine="spark"

    # Цепочка шагов с именами и SAVE: результат пишется в файл
    fa.fugue_sql(f"""
    df  = LOAD "{src}"
    res = SELECT * FROM df WHERE author = 'Иванова'
    SAVE res OVERWRITE "{out}"
    """, engine="duckdb")

    with duckdb.connect() as con:
        print(con.execute(f"SELECT title, units_sold FROM '{out}' ORDER BY title").fetchall())
