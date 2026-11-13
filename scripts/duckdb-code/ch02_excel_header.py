import os
import tempfile

import duckdb

tmp = tempfile.mkdtemp()
xlsx = f"{tmp}/airlines.xlsx"
con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial")
con.sql(f"""
    COPY (SELECT * FROM (VALUES ('SU','Аэрофлот'), ('S7','S7 Airlines')) t(code, name))
    TO '{xlsx}' WITH (FORMAT GDAL, DRIVER 'xlsx')
""")
# AUTO: в файле все значения строки, первая строка считается данными
print(con.sql(f"SELECT * FROM st_read('{xlsx}')").fetchall())
os.environ["OGR_XLSX_HEADERS"] = "FORCE"  # первая строка листа - заголовок
print(con.sql(f"SELECT * FROM st_read('{xlsx}')").fetchall())
