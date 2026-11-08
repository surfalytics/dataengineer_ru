-- Verification queries for the synthetic Yammer dataset (DuckDB).
-- Each query checks one finding from the case answer keys.
--
-- Run:
--   python3 generate_yammer.py /tmp/ts/csv
--   duckdb < yammer_checks.sql        (paths below point to /tmp/ts/csv)

CREATE TABLE yammer_users AS SELECT * FROM read_csv('/tmp/ts/csv/yammer_users.csv', header=true,
  types={'created_at':'TIMESTAMP','activated_at':'TIMESTAMP'});
CREATE TABLE yammer_events AS SELECT * FROM read_csv('/tmp/ts/csv/yammer_events.csv', header=true,
  types={'occurred_at':'TIMESTAMP'});
CREATE TABLE yammer_emails AS SELECT * FROM read_csv('/tmp/ts/csv/yammer_emails.csv', header=true,
  types={'occurred_at':'TIMESTAMP'});
CREATE TABLE yammer_experiments AS SELECT * FROM read_csv('/tmp/ts/csv/yammer_experiments.csv', header=true,
  types={'occurred_at':'TIMESTAMP'});
CREATE TABLE dimension_rollup_periods AS SELECT * FROM read_csv('/tmp/ts/csv/dimension_rollup_periods.csv', header=true,
  types={'time_id':'DATE','pst_start':'TIMESTAMP','pst_end':'TIMESTAMP','utc_start':'TIMESTAMP','utc_end':'TIMESTAMP'});

-- Helper: device class.
CREATE MACRO device_class(d) AS CASE
  WHEN d IN ('iphone 5','iphone 5s','iphone 4s','samsung galaxy s4','nexus 5','htc one',
             'nokia lumia 635','samsung galaxy note','amazon fire phone') THEN 'phone'
  WHEN d IN ('ipad air','ipad mini','nexus 7','nexus 10','kindle fire','samsung galaxy tablet') THEN 'tablet'
  ELSE 'computer' END;

-- Basic integrity: row counts and value sets.
SELECT 'users' t, COUNT(*) n FROM yammer_users UNION ALL
SELECT 'events', COUNT(*) FROM yammer_events UNION ALL
SELECT 'emails', COUNT(*) FROM yammer_emails UNION ALL
SELECT 'experiments', COUNT(*) FROM yammer_experiments UNION ALL
SELECT 'rollup', COUNT(*) FROM dimension_rollup_periods;

SELECT event_type, event_name, COUNT(*) n FROM yammer_events GROUP BY ALL ORDER BY 1, 3 DESC;
SELECT action, COUNT(*) n FROM yammer_emails GROUP BY ALL ORDER BY 2 DESC;

--------------------------------------------------------------------------------
-- CASE 1: A drop in engagement
--------------------------------------------------------------------------------

-- 1.1 The problem chart: weekly engaged users.
-- Expected: grows from May to the end of July (~2,100 in week 2014-07-28),
-- then drops from the week of 2014-08-04 and stays low (~1,700-1,850,
-- about -15 to -20%). The first row (2014-04-28) is a partial week.
SELECT DATE_TRUNC('week', occurred_at) AS week,
       COUNT(DISTINCT user_id) AS weekly_active_users
FROM yammer_events
WHERE event_type = 'engagement'
GROUP BY 1 ORDER BY 1;

-- 1.2 Same metric with the rollup table (period 1007 = rolling 7 days).
-- Expected: the same curve, sampled daily; peak near 2014-08-01, then down.
SELECT p.time_id, COUNT(DISTINCT e.user_id) AS rolling_7d_users
FROM dimension_rollup_periods p
JOIN yammer_events e
  ON e.occurred_at >= p.pst_start AND e.occurred_at < p.pst_end
 AND e.event_type = 'engagement'
WHERE p.period_id = 1007
  AND p.time_id BETWEEN DATE '2014-05-08' AND DATE '2014-09-01'
  AND DAYOFWEEK(p.time_id) = 1   -- one point per week to keep output short
GROUP BY 1 ORDER BY 1;

-- 1.3 Growth: activated users per week, and weekday vs weekend.
-- Expected: steady growth, no drop in August; weekdays much higher than weekends.
SELECT DATE_TRUNC('week', activated_at) AS week,
       COUNT(*) AS activated_users
FROM yammer_users
WHERE activated_at >= '2014-05-01' AND activated_at < '2014-09-01'
GROUP BY 1 ORDER BY 1;

SELECT CASE WHEN DAYOFWEEK(activated_at) IN (0, 6) THEN 'weekend' ELSE 'weekday' END AS day_kind,
       ROUND(COUNT(*) / COUNT(DISTINCT activated_at::DATE), 1) AS avg_activations_per_day
FROM yammer_users
WHERE activated_at >= '2014-05-01' AND activated_at < '2014-09-01'
GROUP BY 1;

-- 1.4 Cohorts by user age (weeks since activation at event time).
-- Expected: users younger than 10 weeks are flat in August; the drop is in
-- the "10+ weeks" cohort (~1,090 -> ~680-740, about -35%).
SELECT DATE_TRUNC('week', e.occurred_at) AS week,
       COUNT(DISTINCT CASE WHEN e.occurred_at - u.activated_at <  INTERVAL 7 DAY THEN e.user_id END) AS age_lt_1w,
       COUNT(DISTINCT CASE WHEN e.occurred_at - u.activated_at >= INTERVAL 7 DAY
                            AND e.occurred_at - u.activated_at <  INTERVAL 28 DAY THEN e.user_id END) AS age_1_3w,
       COUNT(DISTINCT CASE WHEN e.occurred_at - u.activated_at >= INTERVAL 28 DAY
                            AND e.occurred_at - u.activated_at <  INTERVAL 70 DAY THEN e.user_id END) AS age_4_9w,
       COUNT(DISTINCT CASE WHEN e.occurred_at - u.activated_at >= INTERVAL 70 DAY THEN e.user_id END) AS age_10w_plus
FROM yammer_events e
JOIN yammer_users u ON u.user_id = e.user_id
WHERE e.event_type = 'engagement'
GROUP BY 1 ORDER BY 1;

-- 1.5 Weekly engaged users by device class.
-- Expected: phones drop sharply from the week of 2014-08-04 (~620 -> ~400);
-- computers and tablets drop much less.
SELECT DATE_TRUNC('week', occurred_at) AS week,
       COUNT(DISTINCT CASE WHEN device_class(device) = 'computer' THEN user_id END) AS computer,
       COUNT(DISTINCT CASE WHEN device_class(device) = 'phone'    THEN user_id END) AS phone,
       COUNT(DISTINCT CASE WHEN device_class(device) = 'tablet'   THEN user_id END) AS tablet
FROM yammer_events
WHERE event_type = 'engagement'
GROUP BY 1 ORDER BY 1;

-- 1.6 Holiday hypothesis: engaged users by country, July vs August.
-- Expected: the drop is spread over all big countries (no single country).
SELECT location,
       COUNT(DISTINCT CASE WHEN occurred_at >= '2014-07-07' AND occurred_at < '2014-08-04' THEN user_id END) AS jul_4w,
       COUNT(DISTINCT CASE WHEN occurred_at >= '2014-08-04' AND occurred_at < '2014-09-01' THEN user_id END) AS aug_4w,
       ROUND(aug_4w / jul_4w - 1, 2) AS change
FROM yammer_events
WHERE event_type = 'engagement'
GROUP BY 1 HAVING jul_4w >= 50 ORDER BY jul_4w DESC;

-- 1.7 Email actions per week.
-- Expected: sent_weekly_digest keeps growing, email_open is flat,
-- email_clickthrough falls sharply from the week of 2014-08-04.
SELECT DATE_TRUNC('week', occurred_at) AS week,
       COUNT(*) FILTER (WHERE action = 'sent_weekly_digest')      AS weekly_digest,
       COUNT(*) FILTER (WHERE action = 'sent_reengagement_email') AS reengagement,
       COUNT(*) FILTER (WHERE action = 'email_open')              AS opens,
       COUNT(*) FILTER (WHERE action = 'email_clickthrough')      AS clickthroughs
FROM yammer_emails
GROUP BY 1 ORDER BY 1;

-- 1.8 Open and clickthrough rates per email type (open within 5 min of
-- send, click within 5 min of open, as in the original answer query).
-- Expected: open rates flat for both (~46% digest); weekly digest CTR falls
-- from ~60% to ~10% in August; re-engagement CTR stays ~55% (noisy, small).
SELECT DATE_TRUNC('week', e1.occurred_at) AS week,
       ROUND(COUNT(e2.user_id) FILTER (WHERE e1.action = 'sent_weekly_digest')
           / COUNT(*) FILTER (WHERE e1.action = 'sent_weekly_digest'), 3) AS digest_open_rate,
       ROUND(COUNT(e3.user_id) FILTER (WHERE e1.action = 'sent_weekly_digest')
           / COUNT(e2.user_id) FILTER (WHERE e1.action = 'sent_weekly_digest'), 3) AS digest_ctr,
       ROUND(COUNT(e2.user_id) FILTER (WHERE e1.action = 'sent_reengagement_email')
           / COUNT(*) FILTER (WHERE e1.action = 'sent_reengagement_email'), 3) AS reeng_open_rate,
       ROUND(COUNT(e3.user_id) FILTER (WHERE e1.action = 'sent_reengagement_email')
           / NULLIF(COUNT(e2.user_id) FILTER (WHERE e1.action = 'sent_reengagement_email'), 0), 3) AS reeng_ctr
FROM yammer_emails e1
LEFT JOIN yammer_emails e2
  ON e2.user_id = e1.user_id AND e2.action = 'email_open'
 AND e2.occurred_at >= e1.occurred_at AND e2.occurred_at < e1.occurred_at + INTERVAL 5 MINUTE
LEFT JOIN yammer_emails e3
  ON e3.user_id = e2.user_id AND e3.action = 'email_clickthrough'
 AND e3.occurred_at >= e2.occurred_at AND e3.occurred_at < e2.occurred_at + INTERVAL 5 MINUTE
WHERE e1.action IN ('sent_weekly_digest', 'sent_reengagement_email')
GROUP BY 1 ORDER BY 1;

--------------------------------------------------------------------------------
-- CASE 2: Understanding search
-- A session = events of one user with no gap of 10 minutes or more.
--------------------------------------------------------------------------------

CREATE TABLE sessions AS
WITH e AS (
  SELECT user_id, occurred_at, event_name,
         CASE WHEN occurred_at - LAG(occurred_at) OVER (PARTITION BY user_id ORDER BY occurred_at)
                   >= INTERVAL 10 MINUTE
                OR LAG(occurred_at) OVER (PARTITION BY user_id ORDER BY occurred_at) IS NULL
              THEN 1 ELSE 0 END AS new_session
  FROM yammer_events
  WHERE event_type = 'engagement'
), s AS (
  SELECT *, SUM(new_session) OVER (PARTITION BY user_id ORDER BY occurred_at
                                   ROWS UNBOUNDED PRECEDING) AS session_no
  FROM e
)
SELECT user_id, session_no,
       MIN(occurred_at) AS session_start,
       COUNT(*) FILTER (WHERE event_name = 'search_autocomplete')    AS autocompletes,
       COUNT(*) FILTER (WHERE event_name = 'search_run')             AS runs,
       COUNT(*) FILTER (WHERE event_name LIKE 'search_click_result_%') AS clicks
FROM s GROUP BY 1, 2;

-- 2.1 Share of sessions that use autocomplete and full search, by week.
-- Expected: autocomplete ~25% of sessions, search_run ~8%, stable over time.
SELECT DATE_TRUNC('week', session_start) AS week,
       COUNT(*) AS sessions,
       ROUND(AVG(CASE WHEN autocompletes > 0 THEN 1 ELSE 0 END), 3) AS pct_autocomplete,
       ROUND(AVG(CASE WHEN runs > 0 THEN 1 ELSE 0 END), 3)          AS pct_search_run
FROM sessions GROUP BY 1 ORDER BY 1;

SELECT ROUND(AVG(CASE WHEN autocompletes > 0 THEN 1 ELSE 0 END), 3) AS pct_autocomplete,
       ROUND(AVG(CASE WHEN runs > 0 THEN 1 ELSE 0 END), 3)          AS pct_search_run
FROM sessions;

-- 2.2 Autocompletes per session (sessions that use it).
-- Expected: mostly 1 or 2.
SELECT autocompletes, COUNT(*) AS sessions
FROM sessions WHERE autocompletes > 0 GROUP BY 1 ORDER BY 1;

-- 2.3 Full searches per session (sessions that use it).
-- Expected: usually several runs in one session (2-4 is most common).
SELECT runs, COUNT(*) AS sessions
FROM sessions WHERE runs > 0 GROUP BY 1 ORDER BY 1;

-- 2.4 Clicks per session with full search.
-- Expected: most sessions have 0 clicks.
SELECT clicks, COUNT(*) AS sessions
FROM sessions WHERE runs > 0 GROUP BY 1 ORDER BY 1;

-- 2.5 Average clicks by number of runs in the session.
-- Expected: flat; more searches do not bring more clicks.
SELECT runs, COUNT(*) AS sessions, ROUND(AVG(clicks), 2) AS avg_clicks
FROM sessions WHERE runs > 0 GROUP BY 1 ORDER BY 1;

-- 2.6 Clicks by result position.
-- Expected: roughly even across positions 1-10 (bad ranking).
SELECT CAST(REPLACE(event_name, 'search_click_result_', '') AS INT) AS position,
       COUNT(*) AS clicks
FROM yammer_events
WHERE event_name LIKE 'search_click_result_%'
GROUP BY 1 ORDER BY 1;

-- 2.7 Retention of search features: for each user's first session with the
-- feature, how many sessions with the feature in the next 30 days
-- (including the first). Only first sessions before 2014-08-01, so that a
-- full month is visible.
-- Expected: search_run users almost always stop at 1 session;
-- autocomplete users come back to it more often.
WITH firsts AS (
  SELECT user_id,
         MIN(session_start) FILTER (WHERE runs > 0)          AS first_run,
         MIN(session_start) FILTER (WHERE autocompletes > 0) AS first_auto
  FROM sessions GROUP BY 1
), run_ret AS (
  SELECT f.user_id, COUNT(*) AS n_sessions
  FROM firsts f JOIN sessions s ON s.user_id = f.user_id AND s.runs > 0
   AND s.session_start >= f.first_run AND s.session_start < f.first_run + INTERVAL 30 DAY
  WHERE f.first_run < '2014-08-01'
  GROUP BY 1
), auto_ret AS (
  SELECT f.user_id, COUNT(*) AS n_sessions
  FROM firsts f JOIN sessions s ON s.user_id = f.user_id AND s.autocompletes > 0
   AND s.session_start >= f.first_auto AND s.session_start < f.first_auto + INTERVAL 30 DAY
  WHERE f.first_auto < '2014-08-01'
  GROUP BY 1
)
SELECT x.n AS sessions_in_month,   -- 6 means 6 or more
       (SELECT COUNT(*) FROM run_ret r WHERE LEAST(r.n_sessions, 6) = x.n) AS search_run_users,
       (SELECT COUNT(*) FROM auto_ret a WHERE LEAST(a.n_sessions, 6) = x.n) AS autocomplete_users
FROM range(1, 7) x(n)
ORDER BY 1;

--------------------------------------------------------------------------------
-- CASE 3: Validating A/B test results (publisher_update, June 2014)
--------------------------------------------------------------------------------

-- 3.0 One row per user per experiment, all treated in June.
-- Expected: rows = distinct users; dates within 2014-06-01..2014-06-30.
SELECT COUNT(*) AS rows, COUNT(DISTINCT user_id) AS users,
       MIN(occurred_at) AS first_treated, MAX(occurred_at) AS last_treated
FROM yammer_experiments WHERE experiment = 'publisher_update';

-- 3.1 The original result table: messages per user from treatment to July 1.
-- Expected: test group posts ~50% more; t-stat large, p-value ~0.
CREATE TABLE ab_users AS
SELECT ex.user_id, ex.experiment_group, ex.occurred_at AS treated_at,
       u.activated_at,
       CASE WHEN u.activated_at >= '2014-06-01' THEN 'new' ELSE 'existing' END AS user_kind,
       COUNT(e.user_id) FILTER (WHERE e.event_name = 'send_message') AS messages,
       COUNT(e.user_id) FILTER (WHERE e.event_name = 'login')        AS logins,
       COUNT(DISTINCT e.occurred_at::DATE)                           AS days_engaged
FROM yammer_experiments ex
JOIN yammer_users u ON u.user_id = ex.user_id
LEFT JOIN yammer_events e
  ON e.user_id = ex.user_id AND e.event_type = 'engagement'
 AND e.occurred_at >= ex.occurred_at AND e.occurred_at < '2014-07-01'
WHERE ex.experiment = 'publisher_update'
GROUP BY ALL;

CREATE MACRO ab_summary(metric_filter) AS TABLE
WITH g AS (
  SELECT experiment_group, COUNT(*) AS users, SUM(messages) AS total,
         AVG(messages) AS average, STDDEV_SAMP(messages) AS stdev
  FROM ab_users WHERE user_kind IN (SELECT UNNEST(metric_filter)) GROUP BY 1
), c AS (SELECT * FROM g WHERE experiment_group = 'control_group')
SELECT g.experiment_group, g.users,
       SUM(g.users) OVER () AS total_treated_users,
       ROUND(g.users / SUM(g.users) OVER (), 3) AS treatment_percent,
       g.total, ROUND(g.average, 3) AS average,
       ROUND(g.average - c.average, 3) AS rate_difference,
       ROUND(g.average / c.average - 1, 3) AS rate_lift,
       ROUND(g.stdev, 3) AS stdev,
       ROUND((g.average - c.average)
             / SQRT(g.stdev ^ 2 / g.users + c.stdev ^ 2 / c.users), 2) AS t_stat
FROM g CROSS JOIN c ORDER BY 1;

SELECT * FROM ab_summary(['new', 'existing']);

-- 3.2 Other value metrics: logins and days engaged per user.
-- Expected: both higher in the test group ("looks good across the board").
SELECT experiment_group, COUNT(*) AS users,
       ROUND(AVG(messages), 2) AS avg_messages,
       ROUND(AVG(logins), 2) AS avg_logins,
       ROUND(AVG(days_engaged), 2) AS avg_days_engaged
FROM ab_users GROUP BY 1 ORDER BY 1;

-- 3.3 The bug: treatment by user kind.
-- Expected: every new user (activated in June) is in control_group;
-- existing users are split about 50/50.
SELECT user_kind, experiment_group, COUNT(*) AS users,
       ROUND(AVG(messages), 2) AS avg_messages
FROM ab_users GROUP BY 1, 2 ORDER BY 1, 2;

-- 3.4 Fair comparison: existing users only.
-- Expected: lift narrows a lot (from ~55% to ~28%) but stays significant.
SELECT * FROM ab_summary(['existing']);

-- 3.5 Other metrics on existing users only.
-- Expected: test still higher on logins and days engaged, by a smaller margin.
SELECT experiment_group, COUNT(*) AS users,
       ROUND(AVG(messages), 2) AS avg_messages,
       ROUND(AVG(logins), 2) AS avg_logins,
       ROUND(AVG(days_engaged), 2) AS avg_days_engaged
FROM ab_users WHERE user_kind = 'existing' GROUP BY 1 ORDER BY 1;

-- 3.6 Interaction checks for existing users: by device class and by user_type.
-- Expected: the test group is ahead in most cohorts. Two small exceptions:
-- tablets (test 2.95 vs control 3.12, few users) and user_type 3 (1.54 vs 1.49, nearly flat).
SELECT device_class(ex.device) AS device_class, a.experiment_group,
       COUNT(*) AS users, ROUND(AVG(a.messages), 2) AS avg_messages
FROM ab_users a JOIN yammer_experiments ex USING (user_id)
WHERE a.user_kind = 'existing'
GROUP BY 1, 2 ORDER BY 1, 2;

SELECT t.user_type, a.experiment_group,
       COUNT(*) AS users, ROUND(AVG(a.messages), 2) AS avg_messages
FROM ab_users a
JOIN (SELECT DISTINCT user_id, user_type FROM yammer_events) t USING (user_id)
WHERE a.user_kind = 'existing'
GROUP BY 1, 2 ORDER BY 1, 2;
