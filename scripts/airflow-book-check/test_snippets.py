"""Behaviour tests for the Python blocks of the Airflow book summary.
Run by check.sh. Each test imports one extracted block (chNN_i.py) and checks it works."""
import asyncio, importlib, os, sys, uuid
from pathlib import Path
from unittest import mock
import pytest
sys.path.insert(0, os.environ["SNIPPETS_DIR"])

def test_ch07_sensor_callable(tmp_path, monkeypatch):
    m = importlib.import_module("ch07_0")
    real = Path
    monkeypatch.setattr(m, "Path", lambda p: tmp_path if p == "/landing" else real(p))
    d = tmp_path / "partner_a"; d.mkdir()
    assert not m._batch_is_ready("partner_a")
    (d / "part-1.parquet").write_text("x")
    assert not m._batch_is_ready("partner_a")
    (d / "_DONE").write_text("")
    assert m._batch_is_ready("partner_a")

def test_ch08_operator_moves_rows():
    m = importlib.import_module("ch08_0")
    with mock.patch.object(m.PostgresHook, "get_records", return_value=[(1, "a"), (2, "b")]), \
         mock.patch.object(m.S3Hook, "load_file_obj") as up:
        op = m.OrdersToS3Operator(task_id="t", query="select 1", s3_bucket="b", s3_key="k.csv")
        op.execute({})
    body = up.call_args.args[0].read().decode()
    assert body.splitlines() == ["1,a", "2,b"]
    assert up.call_args.kwargs["replace"] is True

def test_ch09_hook_uses_connection():
    m = importlib.import_module("ch09_0")
    conn = mock.Mock(host="api.shop.test", login="u", password="p")
    resp = mock.Mock(); resp.json.return_value = {"items": [1, 2]}
    with mock.patch.object(m.ShopApiHook, "get_connection", return_value=conn), \
         mock.patch("requests.Session.get", return_value=resp) as get:
        h = m.ShopApiHook("shop")
        assert h.get_orders("2025-01-01") == [1, 2]
        assert h.get_orders("2025-01-02") == [1, 2]
    assert get.call_args.args[0] == "https://api.shop.test/orders"

def test_ch09_deferrable():
    from airflow.sdk.exceptions import TaskDeferred
    m = importlib.import_module("ch09_1")
    op = m.WaitForOrdersAsync(task_id="w", conn_id="shop", day="2025-01-01")
    with pytest.raises(TaskDeferred) as e:
        op.execute({})
    trig = e.value.trigger
    assert trig.serialize()[1] == {"conn_id": "shop", "day": "2025-01-01", "pause": 30}
    calls = iter([False, True])
    async def fake(): return next(calls)
    trig._has_orders = fake; trig.pause = 0
    async def first(): return await trig.run().__anext__()
    ev = asyncio.run(first())
    assert ev.payload == {"day": "2025-01-01"}
    op.execute_complete({}, ev.payload)

def test_ch11_pod_settings():
    m = importlib.import_module("ch11_0")
    t = m.clean_in_k8s
    assert t.on_finish_action.value == "delete_pod"

def test_ch13_idempotent_write():
    import pandas as pd, sqlalchemy as sa
    m = importlib.import_module("ch13_0")
    eng = sa.create_engine("sqlite://")
    df = pd.DataFrame({"ride": [1, 2, 3]})
    ts = pd.Timestamp("2026-01-01 10:00")
    m.save_rides(df, eng, ts); m.save_rides(df, eng, ts)
    m.save_rides(df.head(1), eng, pd.Timestamp("2026-01-01 10:15"))
    with eng.connect() as c:
        assert c.execute(sa.text("select count(*) from rides")).scalar() == 4

def test_ch14_chunk_id():
    m = importlib.import_module("ch14_1")
    assert m.chunk_id("борщ") == m.chunk_id("  борщ ")
    assert m.chunk_id("борщ") != m.chunk_id("борщ!")
    uuid.UUID(m.chunk_id("x"))

def test_ch16_fernet(capsys):
    importlib.import_module("ch16_1")
    from cryptography.fernet import Fernet
    key = capsys.readouterr().out.strip()
    assert Fernet(key.encode()).decrypt(Fernet(key.encode()).encrypt(b"s")) == b"s"

def test_ch04_asset_expression():
    m = importlib.import_module("ch04_1")
    assert "AssetAny" in type(m.schedule).__name__
