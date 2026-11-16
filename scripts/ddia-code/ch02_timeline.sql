-- Глава 2: home timeline двумя способами. Запуск: duckdb < ch02_timeline.sql
CREATE TABLE users AS
SELECT * FROM (VALUES (1, 'anna'), (2, 'boris'), (3, 'vera'), (4, 'gleb')) t(id, username);

-- anna читает boris и vera; boris читает vera; gleb читает anna; vera читают трое
CREATE TABLE follows AS
SELECT * FROM (VALUES (1, 2), (1, 3), (2, 3), (4, 1), (4, 3)) t(follower_id, followee_id);

CREATE TABLE posts AS
SELECT * FROM (VALUES
    (101, 2, TIMESTAMP '2026-11-15 09:00', 'Запустили новый pipeline'),
    (102, 3, TIMESTAMP '2026-11-15 09:05', 'p99 вырос до 1,2 с'),
    (103, 4, TIMESTAMP '2026-11-15 09:10', 'Ищу курс по SQL'),
    (104, 3, TIMESTAMP '2026-11-15 09:20', 'Нашли медленный запрос')
) t(id, sender_id, ts, body);

-- Способ 1: считать ленту при каждом чтении (как запрос из книги)
SELECT p.ts, u.username, p.body
FROM posts p
JOIN follows f ON p.sender_id = f.followee_id
JOIN users u   ON p.sender_id = u.id
WHERE f.follower_id = 1          -- лента пользователя anna
ORDER BY p.ts DESC
LIMIT 1000;

-- Способ 2: материализовать ленты заранее (fan-out при записи)
CREATE TABLE home_timeline AS
SELECT f.follower_id AS owner_id, p.id AS post_id, p.ts
FROM posts p JOIN follows f ON p.sender_id = f.followee_id;

-- vera публикует пост: кладём его в ленту каждого подписчика
INSERT INTO posts VALUES (105, 3, TIMESTAMP '2026-11-15 09:30', 'Починили');
INSERT INTO home_timeline
SELECT f.follower_id, 105, TIMESTAMP '2026-11-15 09:30'
FROM follows f WHERE f.followee_id = 3;

-- fan-out = сколько записей в ленты дал один пост
SELECT count(*) AS fan_out FROM home_timeline WHERE post_id = 105;

-- чтение ленты теперь без JOIN по подпискам
SELECT post_id, ts FROM home_timeline WHERE owner_id = 1 ORDER BY ts DESC;
