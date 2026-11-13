"""Глава 7. JupySQL: %sql, %%sql, snippets (--save), %sqlcmd, %sqlplot.
Ядро Jupyter не нужно: магические команды запускаем через IPython.
Данные строим сами во временной папке. Графики пишем в PNG-файл, на странице их нет."""
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import duckdb
from IPython.core.interactiveshell import InteractiveShell

tmp = Path(tempfile.mkdtemp(prefix="duck_ch7_"))
csv = tmp / "airports.csv"
duckdb.sql(f"""COPY (
    SELECT i AS id, ['CA','CA','CA','TX','TX','NY','FL','WA'][1 + (i * 5) % 8] AS state, (i * 13) % 90 AS elev
    FROM range(1, 61) t(i)) TO '{csv}' (HEADER)""")

ip = InteractiveShell.instance()
ip.run_line_magic("load_ext", "sql")
ip.run_line_magic("config", "SqlMagic.displaycon = False")
ip.run_line_magic("config", "SqlMagic.autopandas = False")
ip.run_line_magic("sql", "duckdb://")


def sql(query):
    return ip.run_line_magic("sql", query)


print("1. Запрос к CSV без загрузки (%sql):")
rs = sql(f"SELECT state, count(*) AS n FROM '{csv}' GROUP BY state ORDER BY state")
print(type(rs).__name__, "->", rs.DataFrame().to_dict("records"))

print("\n2. Snippet: --save и --no-execute (%%sql):")
ip.run_cell_magic("sql", "--save state_count --no-execute", f"SELECT state, count(*) AS n FROM '{csv}' GROUP BY state ORDER BY n DESC, state LIMIT 3")
print("snippet не выполнился, но его можно вызвать как таблицу:")
print(sql("SELECT * FROM state_count").DataFrame().to_dict("records"))

print("\n3. Служебные команды (%sqlcmd):")
sql("CREATE TABLE airports AS FROM '" + str(csv) + "'")
tables = ip.run_line_magic("sqlcmd", "tables")
print("tables:", [row[0] for row in tables._table.rows])

print("\n4. График (%sqlplot) строится по маленькой таблице:")
ax = ip.run_line_magic("sqlplot", "bar --table state_count --column state n")
print(type(ax).__name__, "столбцов:", len(ax.patches), "высоты:", [int(p.get_height()) for p in ax.patches])
ax.figure.savefig(tmp / "bar.png")
print("файл графика создан:", (tmp / "bar.png").stat().st_size > 1000)
