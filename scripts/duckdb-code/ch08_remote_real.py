"""Глава 8: примеры из книги по настоящей сети (GitHub и Hugging Face). Нужен интернет.
Данные публичные и не меняются, но если сайт недоступен, скрипт упадёт.
Закрытый датасет не проверяем: нужен личный токен. Секрет создаём с фальшивым токеном."""
import duckdb

con = duckdb.connect()
con.sql("INSTALL httpfs; LOAD httpfs;")

CSV = "https://raw.githubusercontent.com/weimenglee/DuckDB_Book/main/AMZN.csv"
PQ = "https://github.com/weimenglee/DuckDB_Book/raw/main/travel%20insurance.parquet"
HF_TIPS = "hf://datasets/scikit-learn/tips/tips.csv"
HF_ADULT = "hf://datasets/AiresPucrs/adult-census-income/data/train-00000-of-00001-7e70ed54d8cbb057.parquet"


def one(sql):
    return con.sql(sql).fetchone()


print("CSV с GitHub: строк всего, строк за 2018 год:",
      one(f"SELECT count(*), count(*) FILTER (year(Date) = 2018) FROM '{CSV}'"))
print("Parquet с GitHub: число столбцов:",
      one(f"SELECT count(*) FROM (DESCRIBE SELECT * FROM '{PQ}')")[0])
print("Parquet с GitHub: строк, средний возраст:",
      one(f'SELECT count(*), round(avg("Age"), 2) FROM \'{PQ}\''))
print("Hugging Face, tips.csv: первая строка:",
      one(f"SELECT total_bill, tip, sex, day FROM '{HF_TIPS}'"))
print("Hugging Face, Parquet в папке data/: строк:", one(f"SELECT count(*) FROM '{HF_ADULT}'")[0])
print("Hugging Face, glob по двум CSV: строк:",
      one("SELECT count(*) FROM 'hf://datasets/gabrielwu/city_country/*.csv'")[0])
print("Hugging Face, glob по Parquet, question LIKE '%happened%': строк:",
      one("SELECT count(*) FROM 'hf://datasets/Stanford/web_questions/data/*.parquet' "
          "WHERE question LIKE '%happened%'")[0])

con.sql(f"CREATE TABLE tips AS SELECT * FROM '{HF_TIPS}'")
print("Локальная таблица tips (следующие запросы не ходят в сеть): строк:", one("SELECT count(*) FROM tips")[0])

con.sql("CREATE SECRET hf_token (TYPE HUGGINGFACE, TOKEN 'hf_fake_token_for_demo')")
print("Секрет создан (токен фальшивый):", one("SELECT name, type, provider FROM duckdb_secrets()"))
