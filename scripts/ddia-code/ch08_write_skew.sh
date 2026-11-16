#!/usr/bin/env bash
# Глава 8: write skew в PostgreSQL. Два врача одновременно уходят с дежурства.
# Нужен запущенный PostgreSQL 14+, подключение через переменные PGHOST, PGPORT, PGUSER, PGDATABASE.
# Например: docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=pg postgres:17
#           PGHOST=localhost PGUSER=postgres PGPASSWORD=pg bash scripts/ddia-code/ch08_write_skew.sh
set -euo pipefail
export PGOPTIONS="-c client_min_messages=warning"
PSQL=(psql -X -q -At -v ON_ERROR_STOP=0 -v VERBOSITY=terse)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

setup() {
  "${PSQL[@]}" >/dev/null <<'SQL'
DROP TABLE IF EXISTS doctors;
CREATE TABLE doctors (name text PRIMARY KEY, shift_id int, on_call boolean);
INSERT INTO doctors VALUES ('Aaliyah', 1234, true), ('Bryce', 1234, true);
SQL
}

# $1 - врач, $2 - уровень изоляции, $3 - пауза перед UPDATE (секунды)
leave() {
  "${PSQL[@]}" 2>&1 <<SQL | grep -v '^$' | sed -E 's/^(psql:)?[^E]*ERROR: +/ошибка: /'
BEGIN ISOLATION LEVEL $2;
SELECT '$1 видит на дежурстве: ' || count(*) FROM doctors WHERE on_call AND shift_id = 1234;
SELECT pg_sleep($3);
UPDATE doctors SET on_call = false WHERE name = '$1' AND shift_id = 1234;
COMMIT;
SQL
}

for level in "REPEATABLE READ" "SERIALIZABLE"; do
  setup
  leave Aaliyah "$level" 0.5 > "$TMP/a" &
  leave Bryce "$level" 1.0 > "$TMP/b" &
  wait
  echo "== $level"
  cat "$TMP/a" "$TMP/b"
  echo "итог: на дежурстве $("${PSQL[@]}" -c "SELECT count(*) FROM doctors WHERE on_call")"
done
