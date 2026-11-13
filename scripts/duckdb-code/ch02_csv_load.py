"""Глава 2: загрузка CSV тремя способами, ошибка типов и экспорт."""
import os
import tempfile

import duckdb
import pandas as pd

tmp = tempfile.mkdtemp()
src = os.path.join(tmp, "airports.csv")
with open(src, "w", encoding="utf-8") as f:
    f.write("iata_code,airport,city,zip_code\n"
            "SVO,Шереметьево,Москва,00123\n"
            "LED,Пулково,Санкт-Петербург,00456\n"
            "KZN,Казань,Казань,00789\n")

con = duckdb.connect()  # база в памяти

# 1. CREATE TABLE AS: типы определяются сами. DuckDB видит ведущие нули и оставляет VARCHAR.
con.sql(f"CREATE TABLE a_auto AS FROM read_csv_auto('{src}')")
print(con.sql("SELECT column_name, column_type FROM (DESCRIBE a_auto)").fetchall())
print(con.sql("SELECT zip_code FROM a_auto").fetchall())

# 2. all_varchar: все столбцы строки, типы не угадываются.
con.sql(f"CREATE TABLE a_str AS FROM read_csv('{src}', all_varchar=true)")
print(con.sql("SELECT zip_code FROM a_str").fetchall())

# 3. Своя схема + COPY. Вы задаёте тип: INTEGER съедает нули, неподходящий тип даёт ошибку.
con.sql("CREATE TABLE a_copy (iata_code VARCHAR, airport VARCHAR, city VARCHAR, zip_code INTEGER)")
con.sql(f"COPY a_copy FROM '{src}' (HEADER)")
print(con.sql("SELECT zip_code FROM a_copy").fetchall())
con.sql("CREATE TABLE a_bad (iata_code INTEGER, airport VARCHAR, city VARCHAR, zip_code VARCHAR)")
try:
    con.sql(f"COPY a_bad FROM '{src}' (HEADER)")
except duckdb.Error as e:
    print("COPY упал:", type(e).__name__)

# 4. register(): DataFrame виден в SQL как таблица
df = pd.read_csv(src, dtype=str)
con.register("airports_df", df)
print(con.sql("SELECT count(*) FROM airports_df").fetchone())

# 5. Экспорт части данных в CSV без создания таблицы
out = os.path.join(tmp, "two.csv")
con.sql(f"COPY (SELECT iata_code, city FROM read_csv_auto('{src}') LIMIT 2) TO '{out}' (HEADER, DELIMITER ',')")
print(open(out, encoding="utf-8").read().rstrip())
