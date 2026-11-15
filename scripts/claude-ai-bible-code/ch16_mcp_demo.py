#!/usr/bin/env python3
"""Глава 16: подключаемся к MCP server как host и смотрим, что он даёт.
Сервер и клиент работают в одном процессе (in-memory), без Claude и без сети."""
import asyncio
import json
import sys
import warnings
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
warnings.filterwarnings("ignore")  # шум pydantic_settings, на работу не влияет

from mcp.shared.memory import create_connected_server_and_client_session  # noqa: E402

from ch16_mcp_server import mcp  # noqa: E402


def check_config():
    """Читает конфиг host и проверяет least privilege у базы."""
    cfg = json.loads((HERE / "ch16_mcp_config.json").read_text())
    for name, srv in cfg["mcpServers"].items():
        print(f"server {name}: {srv['command']} {srv['args'][1]}")
    user = urlparse(cfg["mcpServers"]["orders-db"]["env"]["DATABASE_URL"]).username
    print("orders-db user:", user, "| read-only:", user.startswith("readonly"))


async def main():
    check_config()
    async with create_connected_server_and_client_session(mcp) as client:
        for t in (await client.list_tools()).tools:
            print("tool:", t.name, "-", t.description.splitlines()[0])
        for r in (await client.list_resources()).resources:
            print("resource:", r.uri)
        for p in (await client.list_prompts()).prompts:
            print("prompt:", p.name)
        for acc in ["acc-001", "acc-999"]:
            res = await client.call_tool("get_subscription", {"account_id": acc})
            print(acc, "->", json.dumps(json.loads(res.content[0].text), ensure_ascii=False))


asyncio.run(main())
