-- DuckDB CLI 1.5.1. Запускайте в пустом рабочем каталоге.
CREATE TEMP TABLE deliveries AS
SELECT i::INTEGER AS delivery_id, 'route-' || (i % 5) AS route, i % 17 AS boxes
FROM range(6144) AS t(i)
ORDER BY delivery_id;

COPY deliveries TO 'deliveries.parquet' (FORMAT PARQUET, ROW_GROUP_SIZE 2048);

SELECT row_group_id, stats_min::INTEGER AS min_id, stats_max::INTEGER AS max_id
FROM parquet_metadata('deliveries.parquet')
WHERE path_in_schema = 'delivery_id'
ORDER BY row_group_id;

SELECT count(*) AS deliveries, sum(boxes) AS boxes
FROM read_parquet('deliveries.parquet')
WHERE delivery_id BETWEEN 5000 AND 5009;
