"""Глава 9. Имитация MotherDuck без аккаунта: вторая база в памяти играет роль облака.
В настоящем облаке было бы ATTACH 'md:my_db' вместо ATTACH ':memory:'."""
import duckdb

con = duckdb.connect()  # «локальная» база

# «Облачная» база с общим справочником: база.схема.таблица
con.execute("ATTACH ':memory:' AS cloud_db")
con.execute("CREATE SCHEMA cloud_db.ref")
con.execute("""
CREATE TABLE cloud_db.ref.airlines AS
SELECT * FROM (VALUES ('AA', 'Air Alpha'), ('BB', 'Blue Bird'), ('CC', 'Cloud Carrier'))
t(iata_code, airline_name)""")

# «Локальные» рейсы. Авиакомпании DD нет в справочнике.
con.execute("""
CREATE TABLE flights AS
SELECT ['AA', 'BB', 'CC', 'DD'][1 + i % 4] AS airline, 1000 + i AS flight_number
FROM range(0, 8) t(i)""")

print("Базы:", [r[0] for r in con.execute("SHOW DATABASES").fetchall()])
print("Полное имя:", con.execute("SELECT count(*) FROM cloud_db.ref.airlines").fetchone()[0], "строки в cloud_db.ref.airlines")

print("Hybrid-запрос: локальные рейсы + справочник из «облака»")
for row in con.execute("""
    SELECT f.airline, f.flight_number, a.airline_name
    FROM flights AS f LEFT JOIN cloud_db.ref.airlines AS a ON f.airline = a.iata_code
    ORDER BY f.flight_number LIMIT 5""").fetchall():
    print("  ", row)

# Запрос в стиле prompt_sql: группы по возрасту. Данные придуманы, зерно фиксировано.
con.execute("""
CREATE TABLE passengers AS
SELECT (hash(i * 7919) % 2)::INT AS survived,
       CASE WHEN i % 11 = 0 THEN NULL ELSE (hash(i) % 80)::INT END AS age
FROM range(0, 500) t(i)""")
print("Запрос из LLM: доля выживших по группам")
for row in con.execute("""
    SELECT CASE WHEN age IS NULL THEN 'Unknown'
                WHEN age < 30 THEN '0-29' WHEN age < 60 THEN '30-59' ELSE '60+' END AS age_group,
           count(*) AS n, round(avg(survived) * 100, 1) AS survival_chance
    FROM passengers GROUP BY age_group ORDER BY age_group""").fetchall():
    print("  ", row)
