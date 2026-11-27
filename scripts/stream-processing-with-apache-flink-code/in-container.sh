#!/usr/bin/env bash
set -euo pipefail
cd /tmp
echo '89418d8b06786b47aae9e04447b2527b2b39b37e1745e2e453b7d930a27ba42b3b6dbc1cbcc21855e7d237b3c12b376c6f41492029fb1550c1200a3d6e51522b  /input/flink.tgz' | sha512sum -c - >&2
echo '1a8dbb2d7e1eee4dfdaf033db5accf0374ec57ae5854dcd00a6e5dd3e980f7f1  /input/examples-scala.jar' | sha256sum -c - >&2
tar -xzf /input/flink.tgz
cd flink-1.7.1
if [[ -n ${1:-} && $1 != operations ]]; then
    source_file=$(basename "$1")
    javac -encoding UTF-8 -cp 'lib/*' -d /tmp "/examples/$source_file"
    if [[ -f /input/derby.jar ]]; then
        echo '2c40eb581e5221ab33c7c796979b49ce404e7e393357c58f7bcdb30a09efca72  /input/derby.jar' | sha256sum -c - >&2
    fi
    exec java -XX:ActiveProcessorCount=2 -cp '/tmp:lib/*:/input/derby.jar' "${source_file%.java}"
fi
# Работаем через loopback. Для проверки масштабирования выделяем два слота.
slots=1
if [[ ${1:-} == operations ]]; then slots=2; fi
sed -i -e 's/^jobmanager.heap.size:.*/jobmanager.heap.size: 320m/' \
       -e 's/^taskmanager.heap.size:.*/taskmanager.heap.size: 512m/' \
       -e "s/^taskmanager.numberOfTaskSlots:.*/taskmanager.numberOfTaskSlots: $slots/" conf/flink-conf.yaml
slot_pattern='"slots-total"[[:space:]]*:[[:space:]]*'${slots}
./bin/start-cluster.sh
trap './bin/stop-cluster.sh >/dev/null 2>&1 || true' EXIT
for ((i=0; i<45; i++)); do
    if curl -fsS http://localhost:8081/overview 2>/dev/null | grep -Eq "$slot_pattern"; then break; fi
    sleep 1
done
curl -fsS http://localhost:8081/overview | grep -Eq "$slot_pattern" || {
    tail -n 20 log/*taskexecutor*.log >&2
    exit 1
}
if [[ ${1:-} == operations ]]; then
    bash /examples/savepoint.sh
    exit
fi
./bin/flink run -d -c io.github.streamingwithflink.chapter1.AverageSensorReadings /input/examples-scala.jar
for ((i=0; i<50; i++)); do
    if grep -h -m 1 'SensorReading(' log/*taskexecutor*.out 2>/dev/null; then exit 0; fi
    sleep 1
done
tail -40 log/*taskexecutor*.log >&2
exit 1
