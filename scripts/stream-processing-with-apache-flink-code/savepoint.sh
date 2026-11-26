#!/usr/bin/env bash
# Запускается из каталога работающего тестового кластера через run.sh ... operations.
set -euo pipefail
curl -fsS http://localhost:8081/overview
echo
main=io.github.streamingwithflink.chapter1.AverageSensorReadings
first=$(./bin/flink run -d -p 1 -c "$main" /input/examples-scala.jar)
job=$(sed -n 's/.*JobID \([a-f0-9]\{32\}\).*/\1/p' <<<"$first")
test -n "$job"
# Сначала дожидаемся результатов работающего задания.
for ((i=0; i<60; i++)); do
    if grep -q 'SensorReading(' log/*taskexecutor*.out 2>/dev/null; then break; fi
    sleep 1
done
grep -q 'SensorReading(' log/*taskexecutor*.out
saved=$(./bin/flink cancel -s file:///tmp/book-savepoints "$job")
printf '%s\n' "$saved"
uri=$(sed -n 's/^.*[Ss]avepoint stored in \(file:[^ ]*\).*$/\1/p' <<<"$saved")
# Клиент 1.7.1 завершает сообщение о savepoint точкой.
uri=${uri%.}
test -f "${uri#file:}/_metadata"
second=$(./bin/flink run -d -p 2 -s "$uri" -c "$main" /input/examples-scala.jar)
resumed=$(sed -n 's/.*JobID \([a-f0-9]\{32\}\).*/\1/p' <<<"$second")
test -n "$resumed"
for ((i=0; i<45; i++)); do
    data=$(curl -fsS "http://localhost:8081/jobs/$resumed")
    if grep -Eq '"status"[[:space:]]*:[[:space:]]*"RUNNING"' <<<"$data" &&
        grep -Eq '"parallelism"[[:space:]]*:[[:space:]]*2' <<<"$data"; then
        printf 'После восстановления: RUNNING, параллелизм 2\n'
        ./bin/flink cancel "$resumed"
        exit 0
    fi
    sleep 1
done
exit 1
