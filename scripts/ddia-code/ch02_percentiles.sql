-- Глава 2: среднее, медиана и перцентили времени ответа. Запуск: duckdb < ch02_percentiles.sql
-- 1000 запросов на двух серверах. Почти все быстрые, редкие очень медленные.
CREATE TABLE requests AS
SELECT
    i AS id,
    CASE WHEN i <= 500 THEN 'a' ELSE 'b' END AS server,
    CASE
        WHEN i % 100 = 0 THEN 3000                -- 1% очень медленных
        WHEN i > 500 AND i % 10 = 0 THEN 900      -- сервер b тормозит чаще
        ELSE 80 + (i * 37) % 120                  -- обычные: 80..199 ms
    END AS response_ms
FROM generate_series(1, 1000) g(i);

SELECT
    round(avg(response_ms))                  AS mean_ms,
    quantile_disc(response_ms, 0.50)         AS p50,
    quantile_disc(response_ms, 0.95)         AS p95,
    quantile_disc(response_ms, 0.99)         AS p99,
    quantile_disc(response_ms, 0.999)        AS p999
FROM requests;

-- Усреднять перцентили серверов нельзя: сравните с p95 по всем запросам
WITH per_server AS (
    SELECT server, quantile_disc(response_ms, 0.95) AS p95
    FROM requests GROUP BY server
)
SELECT
    (SELECT avg(p95) FROM per_server)                       AS avg_of_p95,
    (SELECT quantile_disc(response_ms, 0.95) FROM requests) AS true_p95;
