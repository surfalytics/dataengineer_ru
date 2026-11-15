#!/usr/bin/env python3
"""Глава 18: тот же агент на настоящем Claude Agent SDK.

НЕ запускается без ключа: нужен ANTHROPIC_API_KEY и платный аккаунт API.
Проверено только, что код компилируется: python3 -m py_compile ch18_real_sdk.py
pip install claude-agent-sdk==0.2.182
"""
import asyncio
from pathlib import Path

from claude_agent_sdk import (ClaudeAgentOptions, ClaudeSDKClient, PermissionResultAllow,
                              PermissionResultDeny, ResultMessage, create_sdk_mcp_server, tool)


@tool("read_ticket", "Прочитать полный текст тикета из папки tickets/", {"filename": str})
async def read_ticket(args):
    text = Path("tickets", args["filename"]).read_text(encoding="utf-8")
    return {"content": [{"type": "text", "text": text}]}


@tool("log_summary", "Дописать одну строку итога в triage_log.txt", {"line": str})
async def log_summary(args):
    with open("triage_log.txt", "a", encoding="utf-8") as f:
        f.write(args["line"].rstrip() + "\n")
    return {"content": [{"type": "text", "text": "Записано."}]}


async def can_use_tool(tool_name, tool_input, context):
    # проверка перед каждым вызовом, которому нет разрешения заранее
    if tool_name.endswith("log_summary"):
        return PermissionResultAllow()
    return PermissionResultDeny(message="Это действие не разрешено.")


async def main():
    server = create_sdk_mcp_server(name="triage", tools=[read_ticket, log_summary])
    options = ClaudeAgentOptions(
        model="claude-sonnet-4-6",
        system_prompt=("Ты разбираешь тикеты поддержки. Прочитай тикет, выбери категорию "
                       "(billing, technical, account, other) и срочность (low, medium, high). "
                       "Запиши одну строку: '<файл> | <категория> | <срочность> | <итог>'. "
                       "Не выдумывай того, чего нет в тикете."),
        mcp_servers={"triage": server},
        allowed_tools=["mcp__triage__read_ticket"],   # чтение без вопросов
        tools=[],                                     # встроенные Bash, Edit и др. выключены
        can_use_tool=can_use_tool,                    # запись — через проверку
        max_turns=8,                                  # лимит шагов цикла
        max_budget_usd=0.50,                          # лимит денег на запуск
    )
    async with ClaudeSDKClient(options=options) as client:
        await client.query("Разбери тикет в файле ticket_4471.txt")
        async for message in client.receive_response():
            print(message)                            # журнал всех шагов
            if isinstance(message, ResultMessage):
                print("Итог:", message.result, "| стоимость $", message.total_cost_usd)


if __name__ == "__main__":
    asyncio.run(main())
