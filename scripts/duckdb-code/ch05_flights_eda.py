"""Глава 5. EDA на SQL: доли вместо чисел, отмены, слоты времени, проверка кодов аэропортов.
Рейсы придуманы: 6000 штук, без случайных чисел (hash от номера), поэтому вывод всегда одинаков."""
import duckdb

duckdb.sql("""
    CREATE TABLE airlines AS
    SELECT * FROM (VALUES ('AA', 'Alfa Air'), ('BB', 'Beta Lines'), ('CC', 'Gamma Jet')) t(iata_code, airline)
""")
duckdb.sql("""
    CREATE TABLE flights AS
    WITH base AS (
        SELECT i AS flight_id,
               CASE WHEN hash(i) % 100 < 50 THEN 'AA' WHEN hash(i) % 100 < 80 THEN 'BB' ELSE 'CC' END AS airline,
               1 + CAST(hash(i + 1) % 12 AS INTEGER) AS month,
               1 + CAST(hash(i + 2) % 7 AS INTEGER) AS day_of_week,
               CAST(hash(i + 3) % 24 AS INTEGER) AS dep_hour,
               ['SFO', 'LAX', 'JFK', 'BOS'][1 + CAST(hash(i + 4) % 4 AS INTEGER)] AS origin,
               ['LAX', 'SFO', 'BOS', 'JFK'][1 + CAST(hash(i + 5) % 4 AS INTEGER)] AS destination
        FROM range(6000) t(i)
    )
    SELECT flight_id, airline, month, day_of_week, dep_hour,
           CASE WHEN month = 10 THEN '10397' ELSE origin END AS origin,        -- в октябре коды числовые
           CASE WHEN month = 10 THEN '12892' ELSE destination END AS destination,
           CASE WHEN hash(flight_id + 6) % 100 < 3 THEN 1 ELSE 0 END AS cancelled,
           CASE WHEN hash(flight_id + 7) % 100 <
                     CASE airline WHEN 'AA' THEN 30 WHEN 'BB' THEN 40 ELSE 50 END
                THEN 1 + CAST(hash(flight_id + 8) % 60 AS INTEGER) + CASE WHEN dep_hour >= 18 THEN 25 ELSE 0 END
                ELSE -CAST(hash(flight_id + 9) % 15 AS INTEGER) END AS arrival_delay
    FROM base
""")

print("1. Число задержанных рейсов и доля:")
for row in duckdb.sql("""
    SELECT a.airline, count(*) AS flights,
           sum(CASE WHEN f.arrival_delay > 0 THEN 1 ELSE 0 END) AS delayed,
           round(100.0 * sum(CASE WHEN f.arrival_delay > 0 THEN 1 ELSE 0 END) / count(*), 1) AS delayed_pct
    FROM flights f JOIN airlines a ON f.airline = a.iata_code
    WHERE f.cancelled = 0
    GROUP BY a.airline ORDER BY delayed DESC
""").fetchall():
    print(f"  {row[0]:<11} рейсов {row[1]:>5}  задержано {row[2]:>5}  доля {row[3]}%")

print("2. Доля отмен по авиакомпаниям:")
for name, pct in duckdb.sql("""
    SELECT a.airline, round(sum(f.cancelled) * 100.0 / count(*), 2) AS cancelled_pct
    FROM flights f JOIN airlines a ON f.airline = a.iata_code
    GROUP BY a.airline ORDER BY cancelled_pct DESC
""").fetchall():
    print(f"  {name:<11} {pct}%")

print("3. Средняя задержка по слотам (только задержанные рейсы):")
for slot, avg in duckdb.sql("""
    SELECT CASE WHEN dep_hour < 6 THEN '00-06' WHEN dep_hour < 12 THEN '06-12'
                WHEN dep_hour < 18 THEN '12-18' ELSE '18-24' END AS slot,
           round(avg(arrival_delay), 1)
    FROM flights WHERE cancelled = 0 AND arrival_delay > 0
    GROUP BY slot ORDER BY slot
""").fetchall():
    print(f"  {slot}  {avg} мин")

print("4. Рейсы, где код аэропорта не состоит из букв:")
for month, n in duckdb.sql("""
    SELECT month, count(*) FROM flights
    WHERE origin NOT SIMILAR TO '[A-Za-z]+' OR destination NOT SIMILAR TO '[A-Za-z]+'
    GROUP BY month ORDER BY month
""").fetchall():
    print(f"  месяц {month}: {n} рейсов")
