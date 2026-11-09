-- Собирает учебную базу DuckDB для курса «Базовый минимум SQL».
-- Запускается из build.sh в папке .cache (там лежат raw/ и csv/).
-- Схемы и имена таблиц повторяют SQL Tutorial от ThoughtSpot (бывший Mode):
-- tutorial.* и benn.*. Поэтому запросы из уроков работают без изменений.

CREATE SCHEMA tutorial;
CREATE SCHEMA benn;

-- Вспомогательные макросы: квартал и месяц в виде строк, как в Crunchbase.
CREATE TEMP MACRO ym(d) AS strftime(d, '%Y-%m');
CREATE TEMP MACRO yq(d) AS strftime(d, '%Y') || '-Q' || quarter(d)::varchar;
CREATE TEMP MACRO cat(s) AS lower(replace(split_part(s, '|', 1), ' ', '_'));

---------------------------------------------------------------------------
-- Basic SQL
---------------------------------------------------------------------------

CREATE TABLE tutorial.us_housing_units AS
SELECT year::INTEGER AS year, month::INTEGER AS month, month_name,
       south::DOUBLE AS south, west::DOUBLE AS west, midwest::DOUBLE AS midwest, northeast::DOUBLE AS northeast
FROM read_csv('csv/us_housing_units.csv', header = true);

CREATE TABLE tutorial.billboard_top_100_year_end AS
SELECT year::INTEGER AS year, year_rank::INTEGER AS year_rank, group_name, artist, song_name, id::INTEGER AS id
FROM read_csv('csv/billboard_top_100_year_end.csv', header = true, all_varchar = true);

CREATE TABLE tutorial.aapl_historical_stock_price AS
SELECT date::DATE AS date, year::INTEGER AS year, month::INTEGER AS month,
       open::DOUBLE AS open, high::DOUBLE AS high, low::DOUBLE AS low, close::DOUBLE AS close,
       volume::BIGINT AS volume, id::INTEGER AS id
FROM read_csv('csv/aapl_historical_stock_price.csv', header = true, all_varchar = true);

---------------------------------------------------------------------------
-- Crunchbase (экспорт декабря 2015, CC BY-NC 4.0)
---------------------------------------------------------------------------

CREATE TEMP TABLE raw_companies AS
SELECT * FROM read_csv('raw/companies.csv', header = true, all_varchar = true);
CREATE TEMP TABLE raw_acquisitions AS
SELECT * FROM read_csv('raw/acquisitions.csv', header = true, all_varchar = true);
CREATE TEMP TABLE raw_investments AS
SELECT * FROM read_csv('raw/investments.csv', header = true, all_varchar = true);

CREATE TABLE tutorial.crunchbase_companies AS
SELECT permalink, name, homepage_url,
       cat(category_list) AS category_code,
       TRY_CAST(funding_total_usd AS BIGINT) AS funding_total_usd,
       status, country_code, state_code, region, city,
       TRY_CAST(funding_rounds AS INTEGER) AS funding_rounds,
       founded_at,
       ym(TRY_CAST(founded_at AS DATE)) AS founded_month,
       yq(TRY_CAST(founded_at AS DATE)) AS founded_quarter,
       year(TRY_CAST(founded_at AS DATE)) AS founded_year,
       first_funding_at, last_funding_at
FROM raw_companies;

-- Та же таблица, но founded_at в неудобном формате M/D/YY, а founded_at_clean — чистая строка YYYY-MM-DD.
CREATE VIEW tutorial.crunchbase_companies_clean_date AS
SELECT permalink, name, homepage_url, category_code, funding_total_usd, status, country_code, state_code,
       region, city, funding_rounds,
       strftime(TRY_CAST(founded_at AS DATE), '%-m/%-d/%y') AS founded_at,
       founded_at AS founded_at_clean,
       founded_month, founded_quarter, founded_year, first_funding_at, last_funding_at
FROM tutorial.crunchbase_companies;

CREATE TABLE tutorial.crunchbase_acquisitions AS
SELECT company_permalink, company_name, cat(company_category_list) AS company_category_code,
       company_country_code, company_state_code, company_region, company_city,
       acquirer_permalink, acquirer_name, cat(acquirer_category_list) AS acquirer_category_code,
       acquirer_country_code, acquirer_state_code, acquirer_region, acquirer_city,
       acquired_at,
       ym(TRY_CAST(acquired_at AS DATE)) AS acquired_month,
       yq(TRY_CAST(acquired_at AS DATE)) AS acquired_quarter,
       year(TRY_CAST(acquired_at AS DATE)) AS acquired_year,
       TRY_CAST(price_amount AS DOUBLE) AS price_amount,
       price_currency_code
FROM raw_acquisitions;

CREATE VIEW tutorial.crunchbase_acquisitions_clean_date AS
SELECT company_permalink, company_name, company_category_code, company_country_code, company_state_code,
       company_region, company_city, acquirer_permalink, acquirer_name, acquirer_category_code,
       acquirer_country_code, acquirer_state_code, acquirer_region, acquirer_city,
       strftime(TRY_CAST(acquired_at AS DATE), '%-m/%-d/%y') AS acquired_at,
       TRY_CAST(acquired_at AS TIMESTAMP) AS acquired_at_cleaned,
       acquired_month, acquired_quarter, acquired_year, price_amount, price_currency_code
FROM tutorial.crunchbase_acquisitions;

CREATE TABLE tutorial.crunchbase_investments AS
SELECT company_permalink, company_name, cat(company_category_list) AS company_category_code,
       company_country_code, company_state_code, company_region, company_city,
       investor_permalink, investor_name,
       investor_country_code, investor_state_code, investor_region, investor_city,
       funding_round_type, funding_round_code, funded_at,
       ym(TRY_CAST(funded_at AS DATE)) AS funded_month,
       yq(TRY_CAST(funded_at AS DATE)) AS funded_quarter,
       year(TRY_CAST(funded_at AS DATE)) AS funded_year,
       TRY_CAST(raised_amount_usd AS DOUBLE) AS raised_amount_usd
FROM raw_investments;

-- Две половины таблицы инвестиций — для уроков про UNION.
-- Делим по первой букве компании, чтобы половины были стабильными и не пересекались.
CREATE VIEW tutorial.crunchbase_investments_part1 AS
SELECT * FROM tutorial.crunchbase_investments WHERE lower(company_name) < 'm';
CREATE VIEW tutorial.crunchbase_investments_part2 AS
SELECT * FROM tutorial.crunchbase_investments WHERE lower(company_name) >= 'm' OR company_name IS NULL;

---------------------------------------------------------------------------
-- Инциденты полиции Сан-Франциско, январь 2014
---------------------------------------------------------------------------

CREATE TABLE tutorial.sf_crime_incidents_2014_01 AS
SELECT incidnt_num::BIGINT AS incidnt_num, category, descript, day_of_week,
       date,                                   -- строка: MM/DD/YYYY 08:00:00 AM +0000
       left(time, 5) AS time,                  -- строка: HH:MM
       pd_district, resolution, address,
       lon::DOUBLE AS lon, lat::DOUBLE AS lat, location, id::INTEGER AS id
FROM read_csv('csv/sf_crime_incidents_2014_01.csv', header = true, all_varchar = true);

CREATE VIEW tutorial.sf_crime_incidents_cleandate AS
SELECT *,
       strptime(substr(date, 1, 10) || ' ' || time, '%m/%d/%Y %H:%M') AS cleaned_date
FROM tutorial.sf_crime_incidents_2014_01;

---------------------------------------------------------------------------
-- Прокат велосипедов в Вашингтоне, 1 квартал 2012
---------------------------------------------------------------------------

CREATE TABLE tutorial.dc_bikeshare_q1_2012 AS
SELECT duration, duration_seconds::INTEGER AS duration_seconds,
       start_time::TIMESTAMP AS start_time, start_station, start_terminal::INTEGER AS start_terminal,
       end_time::TIMESTAMP AS end_time, end_station, end_terminal::INTEGER AS end_terminal,
       bike_number, rider_type, id::INTEGER AS id
FROM read_csv('csv/dc_bikeshare_q1_2012.csv', header = true, all_varchar = true);

---------------------------------------------------------------------------
-- Землетрясения в мире по годам (USGS)
---------------------------------------------------------------------------

CREATE TABLE tutorial.worldwide_earthquakes AS
SELECT * FROM read_csv('csv/worldwide_earthquakes.csv', header = true);

---------------------------------------------------------------------------
-- Yammer (выдуманные данные для аналитических кейсов)
---------------------------------------------------------------------------

CREATE TABLE tutorial.yammer_users AS
SELECT user_id::INTEGER AS user_id, created_at::TIMESTAMP AS created_at, company_id::INTEGER AS company_id,
       language, TRY_CAST(activated_at AS TIMESTAMP) AS activated_at, state
FROM read_csv('csv/yammer_users.csv', header = true, all_varchar = true);

CREATE TABLE tutorial.yammer_events AS
SELECT user_id::INTEGER AS user_id, occurred_at::TIMESTAMP AS occurred_at, event_type, event_name,
       location, device, TRY_CAST(user_type AS INTEGER) AS user_type
FROM read_csv('csv/yammer_events.csv', header = true, all_varchar = true);

CREATE TABLE tutorial.yammer_emails AS
SELECT user_id::INTEGER AS user_id, occurred_at::TIMESTAMP AS occurred_at, action,
       TRY_CAST(user_type AS INTEGER) AS user_type
FROM read_csv('csv/yammer_emails.csv', header = true, all_varchar = true);

CREATE TABLE tutorial.yammer_experiments AS
SELECT user_id::INTEGER AS user_id, occurred_at::TIMESTAMP AS occurred_at, experiment, experiment_group,
       location, device
FROM read_csv('csv/yammer_experiments.csv', header = true, all_varchar = true);

CREATE TABLE benn.dimension_rollup_periods AS
SELECT period_id::INTEGER AS period_id, time_id::TIMESTAMP AS time_id,
       pst_start::TIMESTAMP AS pst_start, pst_end::TIMESTAMP AS pst_end,
       utc_start::TIMESTAMP AS utc_start, utc_end::TIMESTAMP AS utc_end
FROM read_csv('csv/dimension_rollup_periods.csv', header = true, all_varchar = true);

---------------------------------------------------------------------------
-- Студенческий американский футбол (школы реальные, игроки выдуманы)
---------------------------------------------------------------------------

CREATE TABLE benn.college_football_teams AS
SELECT division, conference, school_name, roster_url, id::INTEGER AS id
FROM read_csv('csv/college_football_teams.csv', header = true, all_varchar = true);

CREATE TABLE benn.college_football_players AS
SELECT full_school_name, school_name, player_name, position, height::INTEGER AS height,
       weight::INTEGER AS weight, year, hometown, state, id::INTEGER AS id
FROM read_csv('csv/college_football_players.csv', header = true, all_varchar = true);

---------------------------------------------------------------------------
-- Большая таблица событий для урока про производительность (выдуманные данные)
---------------------------------------------------------------------------

CREATE TABLE benn.sample_event_table AS
SELECT i::INTEGER AS event_id,
       (hash(i, 'u') % 50000)::INTEGER + 1 AS user_id,
       DATE '2014-01-01' + (hash(i, 'd') % 181)::INTEGER AS event_date,
       (['login', 'home_page', 'view_inbox', 'send_message', 'like_message', 'search_run'])[(hash(i, 'e') % 6)::INTEGER + 1] AS event_name,
       (['desktop', 'iphone', 'android', 'ipad'])[((hash(i, 'v') >> 16) % 4)::INTEGER + 1] AS device
FROM range(1, 1000001) t(i);

---------------------------------------------------------------------------
-- Описания таблиц и представлений (видны в duckdb_tables() и duckdb_views())
---------------------------------------------------------------------------

COMMENT ON TABLE tutorial.us_housing_units IS 'Новое жильё в США по регионам, тыс. домов в месяц (US Census, 1968-2014)';
COMMENT ON TABLE tutorial.billboard_top_100_year_end IS 'Итоговые годовые чарты Billboard 1956-2013. Одна строка — один исполнитель песни';
COMMENT ON TABLE tutorial.aapl_historical_stock_price IS 'Дневные цены акций Apple 2000-2014';
COMMENT ON TABLE tutorial.crunchbase_companies IS 'Компании из Crunchbase (экспорт 2015, CC BY-NC 4.0)';
COMMENT ON VIEW tutorial.crunchbase_companies_clean_date IS 'Компании Crunchbase: грязная дата founded_at и чистая founded_at_clean';
COMMENT ON TABLE tutorial.crunchbase_acquisitions IS 'Покупки компаний (Crunchbase)';
COMMENT ON VIEW tutorial.crunchbase_acquisitions_clean_date IS 'Покупки компаний: грязная дата acquired_at и чистая acquired_at_cleaned';
COMMENT ON TABLE tutorial.crunchbase_investments IS 'Инвестиции в компании (Crunchbase)';
COMMENT ON VIEW tutorial.crunchbase_investments_part1 IS 'Первая половина crunchbase_investments (для UNION)';
COMMENT ON VIEW tutorial.crunchbase_investments_part2 IS 'Вторая половина crunchbase_investments (для UNION)';
COMMENT ON TABLE tutorial.sf_crime_incidents_2014_01 IS 'Инциденты полиции Сан-Франциско, январь 2014 (SF Open Data). Дата — строкой';
COMMENT ON VIEW tutorial.sf_crime_incidents_cleandate IS 'То же, что sf_crime_incidents_2014_01, плюс cleaned_date (timestamp)';
COMMENT ON TABLE tutorial.dc_bikeshare_q1_2012 IS 'Поездки Capital Bikeshare (Вашингтон), 1 квартал 2012';
COMMENT ON TABLE tutorial.worldwide_earthquakes IS 'Число землетрясений в мире по магнитуде и годам 2000-2012 (каталог USGS)';
COMMENT ON TABLE tutorial.yammer_users IS 'Yammer: пользователи (выдуманные данные для кейсов)';
COMMENT ON TABLE tutorial.yammer_events IS 'Yammer: события в продукте (выдуманные данные)';
COMMENT ON TABLE tutorial.yammer_emails IS 'Yammer: события email-рассылок (выдуманные данные)';
COMMENT ON TABLE tutorial.yammer_experiments IS 'Yammer: участники A/B-тестов (выдуманные данные)';
COMMENT ON TABLE benn.dimension_rollup_periods IS 'Справочник скользящих периодов (period_id 1007 = 7 дней)';
COMMENT ON TABLE benn.college_football_teams IS 'Команды студенческого футбола США (реальные школы, сезон 2013)';
COMMENT ON TABLE benn.college_football_players IS 'Игроки студенческого футбола (выдуманные)';
COMMENT ON TABLE benn.sample_event_table IS 'Большая таблица событий для урока про производительность (выдуманные)';
