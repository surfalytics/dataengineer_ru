-- DuckDB CLI 1.5.1 + DuckLake. Запускайте в пустом рабочем каталоге.
INSTALL ducklake;
LOAD ducklake;
ATTACH 'ducklake::memory:' AS lab (DATA_PATH 'lab_data');

CREATE TABLE lab.stock (item VARCHAR, qty INTEGER);
INSERT INTO lab.stock VALUES ('чай', 8), ('кофе', 12);

SET VARIABLE stock_version = (SELECT max(snapshot_id) FROM lab.snapshots());
SET VARIABLE stock_time = (SELECT max(snapshot_time) FROM lab.snapshots());

UPDATE lab.stock SET qty = 5 WHERE item = 'чай';
SELECT item, qty FROM lab.stock ORDER BY item;

SELECT qty
FROM lab.stock AT (VERSION => getvariable('stock_version'))
WHERE item = 'чай';

SELECT item, qty
FROM lab.stock AT (TIMESTAMP => getvariable('stock_time'))
ORDER BY item;
