#!/usr/bin/env python3
"""Глава 16: минимальный MCP server.
Один read-only tool, один resource и один prompt. Биллинг заменён словарём.
Запуск как сервера (transport stdio): python3 ch16_mcp_server.py
Проверка без Claude: python3 ch16_mcp_demo.py"""
from datetime import date

from mcp.server.fastmcp import FastMCP

# Вместо настоящего API биллинга: две учётные записи в памяти.
BILLING = {
    "acc-001": {"tier": "pro", "renewal_date": date(2026, 12, 1)},
    "acc-002": {"tier": "team", "renewal_date": date(2027, 3, 15)},
}

mcp = FastMCP("subscription-lookup", log_level="WARNING")


@mcp.tool()
def get_subscription(account_id: str) -> dict:
    """Находит текущий тариф клиента и дату продления по ID аккаунта.
    Только чтение. Возвращает tier и renews_on или ошибку, если аккаунта нет."""
    record = BILLING.get(account_id)  # здесь был бы вызов вашего API
    if record is None:
        return {"error": "account not found"}
    return {"tier": record["tier"], "renews_on": record["renewal_date"].isoformat()}


@mcp.resource("billing://tiers")
def list_tiers() -> str:
    """Список тарифов, которые есть в биллинге."""
    return "free, pro, team"


@mcp.prompt()
def renewal_check(account_id: str) -> str:
    """Готовый шаблон: проверить продление подписки."""
    return f"Узнай подписку {account_id} через get_subscription и скажи, когда она продлится."


if __name__ == "__main__":
    mcp.run()  # по умолчанию transport stdio
