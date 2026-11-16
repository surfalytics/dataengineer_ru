-- Глава 13: перевод денег и повтор запроса.
-- Запуск: duckdb < scripts/ddia-code/ch13_request_id.sql

-- 1. Перевод без идентификатора запроса: повтор списывает деньги дважды.
CREATE TABLE accounts (account_id INTEGER PRIMARY KEY, balance DECIMAL(10,2));
INSERT INTO accounts VALUES (1234, 100.00), (4321, 100.00);

BEGIN TRANSACTION;
UPDATE accounts SET balance = balance + 11.00 WHERE account_id = 1234;
UPDATE accounts SET balance = balance - 11.00 WHERE account_id = 4321;
COMMIT;
-- Клиент не получил ответ на COMMIT и повторил ту же транзакцию.
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance + 11.00 WHERE account_id = 1234;
UPDATE accounts SET balance = balance - 11.00 WHERE account_id = 4321;
COMMIT;

SELECT 'без request_id' AS вариант, account_id, balance FROM accounts ORDER BY account_id;

-- 2. Тот же перевод с уникальным request_id.
UPDATE accounts SET balance = 100.00;
CREATE TABLE requests (
    request_id   VARCHAR PRIMARY KEY,  -- уникальный ключ запроса от клиента
    from_account INTEGER,
    to_account   INTEGER,
    amount       DECIMAL(10,2)
);

BEGIN TRANSACTION;
INSERT INTO requests VALUES ('0286fdb8-d7e1-423f-b40b-792b3608036c', 4321, 1234, 11.00);
UPDATE accounts SET balance = balance + 11.00 WHERE account_id = 1234;
UPDATE accounts SET balance = balance - 11.00 WHERE account_id = 4321;
COMMIT;
-- Повтор с тем же request_id: INSERT падает, COMMIT откатывает транзакцию.
BEGIN TRANSACTION;
INSERT INTO requests VALUES ('0286fdb8-d7e1-423f-b40b-792b3608036c', 4321, 1234, 11.00);
UPDATE accounts SET balance = balance + 11.00 WHERE account_id = 1234;
UPDATE accounts SET balance = balance - 11.00 WHERE account_id = 4321;
COMMIT;

SELECT 'с request_id' AS вариант, account_id, balance FROM accounts ORDER BY account_id;
SELECT count(*) AS запросов FROM requests;
