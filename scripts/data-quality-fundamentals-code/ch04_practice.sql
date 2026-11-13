-- Периоды без загрузки (в эти дни данных нет) и дни, когда avg_temp почти вся NULL
CREATE TABLE gaps(first_missing DATE, last_missing DATE);
INSERT INTO gaps VALUES
  ('2024-02-03','2024-02-09'), ('2024-03-20','2024-03-22'), ('2024-05-11','2024-05-17'),
  ('2024-06-04','2024-06-05'), ('2024-06-18','2024-06-21'), ('2024-07-08','2024-07-09');
CREATE TABLE spikes(day DATE);
INSERT INTO spikes VALUES ('2024-04-09'), ('2024-07-23'), ('2024-07-24'), ('2024-07-25');

-- Основная таблица: 85-114 строк в день, доля NULL в avg_temp около 30%
CREATE TABLE planets AS
SELECT d.day || '-' || n AS id, d.day AS date_added,
       CASE WHEN (hash(d.day || '-' || n || 't') % 1000) / 1000.0
                 < CASE WHEN d.day IN (SELECT day FROM spikes) THEN 0.95 ELSE 0.3 END
            THEN NULL
            ELSE 200 + (hash(d.day || '-' || n || 'v') % 400) END AS avg_temp
FROM (SELECT CAST(range AS DATE) AS day FROM range(DATE '2024-01-01', DATE '2024-09-07', INTERVAL 1 DAY)) d
CROSS JOIN LATERAL (SELECT unnest(range(1, 86 + (hash(d.day::VARCHAR) % 30)::INT)) AS n)
WHERE NOT EXISTS (SELECT 1 FROM gaps g WHERE d.day BETWEEN g.first_missing AND g.last_missing);

-- Потребитель: с 5 августа половина значений habitability ломается и становится 0
CREATE TABLE habitables AS
SELECT id, date_added,
       CASE WHEN date_added >= DATE '2024-08-05' AND hash(id || 'z') % 100 < 50 THEN 0.0
            ELSE (hash(id || 'h') % 999 + 1) / 1000.0 END AS habitability
FROM planets;

-- Снимок списка колонок planets по дням и метки настоящих инцидентов свежести
CREATE TABLE schema_log AS
SELECT day, CASE WHEN day < DATE '2024-08-05' THEN 'id,avg_temp,date_added'
                 ELSE 'id,avg_temp,date_added,eccentricity,atmosphere' END AS cols
FROM (SELECT CAST(range AS DATE) AS day FROM range(DATE '2024-01-01', DATE '2024-09-07', INTERVAL 1 DAY));
CREATE TABLE incidents(day DATE);
INSERT INTO incidents VALUES ('2024-02-10'), ('2024-05-18'), ('2024-06-22'), ('2024-07-10');

SELECT id FROM planets GROUP BY id HAVING count(*) > 1;
SELECT count(*) AS rows_total, count(DISTINCT date_added) AS load_days FROM planets;

CREATE VIEW freshness AS
SELECT date_added,
       date_diff('day', lag(date_added) OVER (ORDER BY date_added), date_added) AS days_since_last_update
FROM (SELECT DISTINCT date_added FROM planets);

SELECT * FROM freshness WHERE days_since_last_update > 1 ORDER BY date_added;

SELECT date_trunc('month', date_added)::DATE AS month, round(avg(habitability), 3) AS avg_habitability
FROM habitables GROUP BY month ORDER BY month;

WITH t AS (SELECT range AS threshold FROM range(1, 8)),
scored AS (
  SELECT t.threshold,
         count(*) FILTER (WHERE f.days_since_last_update > t.threshold AND i.day IS NOT NULL) AS tp,
         count(*) FILTER (WHERE f.days_since_last_update > t.threshold AND i.day IS NULL) AS fp,
         count(*) FILTER (WHERE f.days_since_last_update <= t.threshold AND i.day IS NOT NULL) AS fn
  FROM t CROSS JOIN freshness f LEFT JOIN incidents i ON i.day = f.date_added
  WHERE f.days_since_last_update > 1
  GROUP BY t.threshold)
SELECT threshold, tp, fp, fn,
       round(tp / (tp + fp), 2) AS precision, round(tp / (tp + fn), 2) AS recall,
       round(2 * tp / (2 * tp + fp + fn), 3) AS f1
FROM scored ORDER BY threshold;

WITH rates AS (
  SELECT date_added, avg((avg_temp IS NULL)::INT) AS null_rate FROM planets GROUP BY date_added),
w AS (
  SELECT *, avg(null_rate) OVER (ORDER BY date_added ROWS BETWEEN 14 PRECEDING AND 1 PRECEDING) AS rolling
  FROM rates),
alerts AS (
  SELECT date_added, null_rate, rolling,
         date_diff('day', lag(date_added) OVER (ORDER BY date_added), date_added) AS days_since_prev_alert
  FROM w WHERE null_rate - rolling > 0.3)
SELECT date_added, round(null_rate, 3) AS null_rate, round(rolling, 3) AS rolling
FROM alerts WHERE days_since_prev_alert IS NULL OR days_since_prev_alert > 1 ORDER BY date_added;

WITH changes AS (
  SELECT day, cols, lag(cols) OVER (ORDER BY day) AS past_cols FROM schema_log),
zero_rate AS (
  SELECT date_added, avg((habitability = 0)::INT) AS zr FROM habitables GROUP BY date_added)
SELECT (SELECT min(day) FROM changes WHERE cols <> past_cols) AS schema_changed_on,
       (SELECT min(date_added) FROM zero_rate WHERE zr > 0) AS zero_rate_started_on;
