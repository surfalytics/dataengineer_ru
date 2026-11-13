"""Глава 13: запись в базу. append даёт дубли при повторе, DELETE + INSERT в транзакции не даёт.
SQLite в памяти вместо PostgreSQL. Запуск: python3 -I ch13_idempotent_write.py (нужны pandas, sqlalchemy)"""
import pandas as pd
import sqlalchemy as sa

df = pd.DataFrame({"start_location_id": [230, 48], "end_location_id": [68, 239], "tripduration": [632, 698]})
run_ts = pd.Timestamp("2024-09-19 19:15:00")


def count(engine, table):
    with engine.connect() as conn:
        return conn.execute(sa.text(f"SELECT COUNT(*) FROM {table}")).scalar()


def save_rides(df, engine, run_ts):
    """Replace all rows of one run, then insert fresh rows."""
    df = df.assign(run_ts=run_ts)
    with engine.begin() as conn:  # one transaction
        if sa.inspect(conn).has_table("rides"):
            delete = sa.text("DELETE FROM rides WHERE run_ts = :ts").bindparams(
                sa.bindparam("ts", type_=sa.DateTime)
            )
            conn.execute(delete, {"ts": run_ts.to_pydatetime()})
        df.to_sql("rides", con=conn, index=False, if_exists="append")


naive = sa.create_engine("sqlite://")
for _ in range(2):
    df.to_sql("rides_append", con=naive, index=False, if_exists="append")
print("append, 2 запуска:", count(naive, "rides_append"), "строк")

safe = sa.create_engine("sqlite://")
for _ in range(2):
    save_rides(df, safe, run_ts)
print("DELETE + INSERT, 2 запуска:", count(safe, "rides"), "строк")
