#!/usr/bin/env bash
# Check the Python examples of the Airflow book summary on a real Airflow 3.
# 1. Every block imports (DAG files load in DagBag, no import errors, no deprecation warnings).
# 2. Local DAGs pass `airflow dags test`.
# 3. Behaviour tests (pytest) for hooks, operators, triggers and helper functions.
# Needs: uv. Usage (from repo root): scripts/airflow-book-check/check.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="${WORK:-${TMPDIR:-/tmp}/airflow-book-check}"
VENV="$WORK/venv"
AIRFLOW_VERSION="${AIRFLOW_VERSION:-3.4.0}"
export AIRFLOW_HOME="$WORK/home" AIRFLOW__CORE__LOAD_EXAMPLES=False AIRFLOW__CORE__DAGS_FOLDER="$WORK/dags"
export SNIPPETS_DIR="$WORK/snippets"

if [ ! -x "$VENV/bin/airflow" ]; then
  uv venv -q -p 3.12 "$VENV"
  uv pip install -q -p "$VENV/bin/python" "apache-airflow[standard]==$AIRFLOW_VERSION" pandas pytest \
    apache-airflow-providers-docker apache-airflow-providers-postgres apache-airflow-providers-amazon \
    apache-airflow-providers-cncf-kubernetes apache-airflow-providers-common-messaging \
    apache-airflow-providers-apache-kafka apache-airflow-providers-http
fi
PY="$VENV/bin/python"
rm -rf "$SNIPPETS_DIR" "$AIRFLOW__CORE__DAGS_FOLDER"; mkdir -p "$AIRFLOW__CORE__DAGS_FOLDER"
python3 "$HERE/extract.py" "$SNIPPETS_DIR"
"$VENV/bin/airflow" db migrate >/dev/null 2>&1

echo "== 1. Import every block"
fail=0
for f in "$SNIPPETS_DIR"/*.py; do
  out=$("$PY" -W always "$HERE/load_one.py" "$f" 2>&1) || { echo "FAIL $(basename "$f")"; echo "$out" | tail -5; fail=1; continue; }
  if echo "$out" | grep -i "deprecat" | grep -v -E "determine_kwargs|Cadwyn" >/dev/null; then
    echo "DEPRECATED $(basename "$f")"; echo "$out" | grep -i deprecat | head -2; fail=1
  else
    echo "ok   $(basename "$f"): $(echo "$out" | tail -1)"
  fi
done

echo "== 2. airflow dags test"
# chapter block -> dag_id. Others need Docker, Kubernetes, Kafka, S3 or an API.
LOCAL="ch01_0:demo_weather_board ch02_0:demo_news_words ch03_0:demo_daily_clicks ch04_0:orders_producer
ch05_0:weather_templating ch06_0:sales_branching ch12_0:mapping_demo ch13_1:nyc_rides ch15_0:nightly_export
ch17_0:check_image_libs"
for p in $LOCAL; do cp "$SNIPPETS_DIR/${p%%:*}.py" "$AIRFLOW__CORE__DAGS_FOLDER/"; done
"$VENV/bin/airflow" dags reserialize >/dev/null 2>&1
for p in $LOCAL; do
  dag="${p##*:}"
  log=$("$VENV/bin/airflow" dags test "$dag" 2026-01-02 2>&1 || true)
  if grep "DagRun Finished: dag_id=$dag," <<<"$log" | grep -q "state=success"; then
    echo "ok   $dag"
  else
    echo "FAIL $dag"; fail=1
  fi
done

# ch04: the producer run must store an asset event with extra["day"].
"$PY" - <<'PYEOF' && echo "ok   ch04 asset event has extra" || { echo "FAIL ch04 asset extra"; fail=1; }
from airflow.models.asset import AssetEvent
from airflow.utils.session import create_session
with create_session() as s:
    ev = s.query(AssetEvent).order_by(AssetEvent.id.desc()).first()
    assert ev and ev.extra.get("day") == "2026-01-02", ev and ev.extra
PYEOF
# ch05: `airflow tasks render` prints the rendered template.
log=$("$VENV/bin/airflow" tasks render weather_templating download 2026-01-05 2>&1 || true)
if grep -q "weather-20260105" <<<"$log"; then
  echo "ok   ch05 tasks render"; else echo "FAIL ch05 tasks render"; fail=1; fi

echo "== 3. pytest"
mkdir -p "$WORK/proj/dags" "$WORK/proj/tests"
cp "$SNIPPETS_DIR/ch01_0.py" "$SNIPPETS_DIR/ch06_0.py" "$WORK/proj/dags/"
cp "$SNIPPETS_DIR/ch10_0.py" "$WORK/proj/tests/test_dag_integrity.py"
cp "$SNIPPETS_DIR/ch10_1.py" "$WORK/proj/tests/test_report_operator.py"
"$PY" -m pytest -q -p no:cacheprovider "$HERE/test_snippets.py" "$WORK/proj/tests" || fail=1

[ "$fail" = 0 ] && echo "ALL OK" || { echo "SOME CHECKS FAILED"; exit 1; }
