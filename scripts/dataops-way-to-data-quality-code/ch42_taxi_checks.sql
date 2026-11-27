-- Run in DuckDB after setting taxi_file to the local January 2024 Parquet file.
WITH trips AS (
    SELECT * FROM read_parquet(getvariable('taxi_file'))
)
SELECT
    count(*) AS rows_total,
    count(*) FILTER (WHERE passenger_count IS NULL OR passenger_count < 1) AS passengers,
    count(*) FILTER (WHERE payment_type NOT IN (1, 2, 3, 4, 5, 6)) AS payment_code,
    count(*) FILTER (WHERE trip_distance <= 0 OR trip_distance > 1000) AS distance,
    count(*) FILTER (WHERE fare_amount < 0) AS negative_fare,
    count(*) FILTER (WHERE total_amount < 0) AS negative_total,
    count(*) FILTER (WHERE tpep_dropoff_datetime < tpep_pickup_datetime) AS trip_order,
    count(*) FILTER (WHERE tpep_pickup_datetime < '2024-01-01'
                         OR tpep_pickup_datetime >= '2024-02-01') AS pickup_month
FROM trips;
