"""Глава 2: почему code execution экономит токены в MCP.
Сравниваем два режима на одной задаче «найди книгу и посчитай её продажи»:
  - прямые вызовы: в context window заранее грузятся описания ВСЕХ инструментов,
    а промежуточные результаты (сырые строки продаж) проходят через модель;
  - code execution: модель видит только дерево имён инструментов, читает описания
    двух нужных и пишет код; сырые строки остаются в sandbox, в модель идёт итог.
Токены считаем грубо: 1 токен ≈ 4 символа. Данные выдуманные, seed фиксирован.
Запуск: python3 -I scripts/redefining-de-ai-code/ch02_tool_tokens.py   (только стандартная библиотека)"""
import json
import random

random.seed(42)


def tokens(obj):
    text = obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False)
    return len(text) // 4


def tool_def(name, area):
    """Описание инструмента в стиле MCP: имя, описание, JSON Schema входа."""
    return {
        "name": name,
        "description": f"Инструмент отдела «{area}»: ищет записи по фильтрам и возвращает список словарей.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "book_id": {"type": "string", "description": "ID книги, например B001"},
                "region": {"type": "string", "description": "Регион продаж"},
                "channel": {"type": "string", "description": "Канал: магазин, сайт, партнёр"},
                "limit": {"type": "integer", "description": "Сколько строк вернуть, 1-100"},
            },
        },
    }


areas = ["каталог", "продажи", "склад", "кадры", "финансы", "закупки", "события", "ремонт"]
sales_rows = [{"book_id": "B001", "region": random.choice(["Север", "Юг", "Запад"]),
               "channel": random.choice(["магазин", "сайт"]), "qty": random.randint(1, 5),
               "price": 17.5} for _ in range(300)]
summary = {"book_id": "B001", "rows": len(sales_rows),
           "copies": sum(r["qty"] for r in sales_rows),
           "revenue": round(sum(r["qty"] * r["price"] for r in sales_rows), 2)}

print(f"{'инструментов':>12} | {'прямые вызовы':>13} | {'code execution':>14} | экономия")
for n_tools in (8, 50, 200):
    tools = [tool_def(f"{areas[i % len(areas)]}_{i:03d}", areas[i % len(areas)]) for i in range(n_tools)]
    # Прямые вызовы: все описания + сырые строки продаж проходят через модель.
    direct = tokens(tools) + tokens(sales_rows) + tokens(summary)
    # Code execution: дерево имён + 2 нужных описания + код + только итог.
    tree = "\n".join(t["name"] for t in tools)
    code = "rows = sales.search(book_id='B001', limit=100)\nprint(summarize(rows))"
    smart = tokens(tree) + tokens(tools[:2]) + tokens(code) + tokens(summary)
    print(f"{n_tools:>12} | {direct:>13} | {smart:>14} | {100 * (1 - smart / direct):.1f}%")
print("итог, который видит модель в обоих режимах:", summary)
