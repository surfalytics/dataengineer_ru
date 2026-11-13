"""Глава 5. Расширение spatial: точка из широты и долготы, ST_DWithin и ST_Distance.
Координаты аэропортов Флориды и ещё нескольких городов взяты округлённо из открытых источников."""
import duckdb

duckdb.sql("INSTALL spatial; LOAD spatial;")
duckdb.sql("""
    CREATE TABLE airports AS
    SELECT iata, city, state, lat, lng, ST_Point(lng, lat) AS geom  -- сначала долгота, потом широта
    FROM (VALUES
        ('MIA', 'Miami',          'FL', 25.79, -80.29),
        ('FLL', 'Fort Lauderdale','FL', 26.07, -80.15),
        ('PBI', 'West Palm Beach','FL', 26.68, -80.10),
        ('RSW', 'Fort Myers',     'FL', 26.54, -81.76),
        ('MCO', 'Orlando',        'FL', 28.43, -81.31),
        ('TPA', 'Tampa',          'FL', 27.98, -82.53),
        ('JAX', 'Jacksonville',   'FL', 30.49, -81.69),
        ('ATL', 'Atlanta',        'GA', 33.64, -84.43),
        ('JFK', 'New York',       'NY', 40.64, -73.78),
        ('LAX', 'Los Angeles',    'CA', 33.94, -118.41)
    ) t(iata, city, state, lat, lng)
""")

miami = "ST_Point(-80.2706578, 25.7824017)"  # точка в Майами, как в книге

print("WKT первой точки:", duckdb.sql("SELECT ST_AsText(geom) FROM airports WHERE iata = 'MIA'").fetchone()[0])
for deg in (2, 3):
    n = duckdb.sql(f"SELECT count(*) FROM airports WHERE ST_DWithin(geom, {miami}, {deg})").fetchone()[0]
    print(f"Радиус {deg} градуса вокруг Майами, аэропортов: {n}")

print("Три ближайших:")
for iata, city, d in duckdb.sql(f"""
    SELECT iata, city, round(ST_Distance(geom, {miami}), 3) AS dist_deg
    FROM airports ORDER BY dist_deg LIMIT 3
""").fetchall():
    print(f"  {iata}  {city:<16} {d} градуса")
