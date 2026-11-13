"""Глава 9: проверка без сервера. API заменён заглушкой, Connection тоже.
Запуск: $VENV/bin/python -I ch09_check.py (нужен apache-airflow 3.4.0)."""
import asyncio
import contextlib
import io
import json
import logging
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

logging.disable(logging.CRITICAL)
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ch09_components as c  # noqa: E402
from airflow.sdk import DAG  # noqa: E402
from airflow.sdk.exceptions import TaskDeferred  # noqa: E402

def quiet(fn, *args):
    """Airflow пишет предупреждение в stdout: прячем его."""
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args)


ORDERS = {"2026-01-02": [{"id": i, "amount": 10 * i} for i in range(1, 8)]}  # 7 заказов


class FakeSession:
    """Заглушка requests.Session: страницы по offset и limit."""
    calls = []

    def get(self, url, params):
        FakeSession.calls.append((params["offset"], params["limit"]))
        items = ORDERS.get(params["day"], [])
        page = items[params["offset"]: params["offset"] + params["limit"]]
        return SimpleNamespace(raise_for_status=lambda: None, json=lambda: {"items": page, "total": len(items)})

    def close(self):
        pass


conn = SimpleNamespace(host="shop.example", login="u", password="p")
patches = [
    mock.patch.object(c.requests, "Session", FakeSession),
    mock.patch.object(c.OrdersHook, "get_connection", return_value=conn),
]
with contextlib.ExitStack() as st:
    for p in patches:
        st.enter_context(p)
    # 1. hook: пагинация и кэш соединения
    hook = c.OrdersHook("shop_api")
    got = list(hook.get_orders("2026-01-02", batch_size=3))
    print("hook: заказов", len(got), "| страницы (offset, limit):", FakeSession.calls)
    print("hook: пустой день ->", list(hook.get_orders("2026-01-03")))

    # 2. operator: шаблоны и запись файла
    with DAG("d", schedule=None) as dag:
        with tempfile.TemporaryDirectory() as tmp:
            op = c.OrdersFetchOperator(task_id="fetch", conn_id="shop_api", output_path=f"{tmp}/{{{{ ds }}}}.json")
            op.render_template_fields({"ds": "2026-01-02"})
            print("operator: day =", op.day, "| файл =", Path(op.output_path).name)
            n = quiet(op.execute, {})
            print("operator: записано", n, "заказов, в файле", len(json.loads(Path(op.output_path).read_text())))

    # 3. sensor: poke
    with DAG("d2", schedule=None):
        s = c.OrdersSensor(task_id="s", conn_id="shop_api", day="2026-01-03")
        print("sensor: пустой день, poke =", s.poke({}))
        s.day = "2026-01-02"
        print("sensor: есть заказы, poke =", s.poke({}))

    # 4. deferrable: defer, serialize, run
    with DAG("d3", schedule=None):
        a = c.OrdersSensorAsync(task_id="a", conn_id="shop_api", day="2026-01-02")
        try:
            quiet(a.execute, {})
        except TaskDeferred as e:
            print("defer: method_name =", e.method_name, "| trigger =", type(e.trigger).__name__)
    trig = c.OrdersTrigger("shop_api", "2026-01-02", pause=0)
    print("serialize:", trig.serialize()[0], sorted(trig.serialize()[1]))

    answers = iter([False, False, True])  # заказы появляются на третьей проверке
    checks = []

    async def fake_has(self):
        checks.append(1)
        return next(answers)

    async def run_trigger():
        with mock.patch.object(c.OrdersTrigger, "_has_orders", fake_has):
            return [ev async for ev in trig.run()]

    events = asyncio.run(run_trigger())
    print("trigger: проверок", len(checks), "| событие:", events[0].payload)

# 5. DAG-файл: разбор через DagBag
from airflow.dag_processing.dagbag import DagBag  # noqa: E402

with contextlib.redirect_stdout(io.StringIO()):
    bag = DagBag(dag_folder=str(HERE / "ch09_dag.py"))
d = bag.dags["orders_custom"]
print("DagBag: ошибки импорта:", bag.import_errors or "нет")
print("DagBag: tasks =", sorted(d.task_dict), "| upstream fetch_orders =", sorted(d.task_dict["fetch_orders"].upstream_task_ids))
