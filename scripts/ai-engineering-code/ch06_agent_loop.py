"""Глава 6: цикл агента: план -> проверка плана -> выполнение tools -> наблюдение -> reflection.
Мини-агент магазина «Kitty Vogue» работает с настоящей базой SQLite (в памяти). Планировщик и text-to-SQL
здесь mock (простые правила), всё остальное — настоящее: SQL, проверка плана, журнал шагов, разбор ошибки.
В реальной системе planner() и text_to_sql() заменяют вызовами модели.
Показывает: план на естественном языке и translator, проверку плана до запуска, трассу в стиле ReAct,
reflection и исправление ошибки SQL, параллельные шаги (разница в latency) и ограничение числа шагов.
Запуск: python3 -I scripts/ai-engineering-code/ch06_agent_loop.py   (только стандартная библиотека)"""
import difflib
import random
import sqlite3
from datetime import date, timedelta

TODAY = date(2030, 9, 13)  # «сегодня» зафиксировано, чтобы вывод не менялся
rng = random.Random(3)
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE sales (order_id INT, sold_on TEXT, product TEXT, price REAL, units INT)")
PRICES = {"Fruity Fedora": 18.0, "Meow Mix Seasoning": 10.99, "Purr & Shake": 25.0, "Tabby Tie": 7.5, "Whisker Scarf": 12.0}
weights = {"Fruity Fedora": 5, "Meow Mix Seasoning": 3, "Purr & Shake": 2, "Tabby Tie": 1, "Whisker Scarf": 1}
for oid in range(1, 301):
    product = rng.choices(list(weights), weights=list(weights.values()))[0]
    day = TODAY - timedelta(days=rng.randint(0, 19))
    db.execute("INSERT INTO sales VALUES (?, ?, ?, ?, ?)", (oid, day.isoformat(), product, PRICES[product], rng.randint(1, 3)))
print(f"в таблице sales строк: {db.execute('SELECT count(*) FROM sales').fetchone()[0]}, «сегодня»: {TODAY}")

# ---------------------------------------------------------------- tools
CALLS = []  # журнал всех вызовов: имя, аргументы, результат


def tool(fn):
    def wrapper(*a, **kw):
        out = fn(*a, **kw)
        CALLS.append((fn.__name__, a or kw, out))
        return out
    wrapper.__name__ = fn.__name__
    return wrapper


@tool
def get_today_date():
    return TODAY.isoformat()


@tool
def run_sql(query):
    return db.execute(query).fetchall()  # при ошибке SQL бросит исключение — его увидит reflection


@tool
def fetch_product_info(product_name):
    return {"product": product_name, "price": PRICES[product_name]}


def text_to_sql(question, hint=None):
    """MOCK: шаблонный text-to-SQL. Первая попытка нарочно ошибается в имени колонки."""
    col = "product" if hint else "product_name"
    if "top product" in question:
        return f"SELECT {col}, SUM(units) AS u FROM sales WHERE sold_on >= '{(TODAY - timedelta(days=6)).isoformat()}' GROUP BY {col} ORDER BY u DESC LIMIT 1"
    return (f"SELECT SUM(units) FROM sales WHERE {col} = 'Fruity Fedora' "
            f"AND sold_on >= '{(TODAY - timedelta(days=7)).isoformat()}'")


# ---------------------------------------------------------------- planner (mock) + проверка плана
KNOWN_ACTIONS = {"get current date", "find top product of the last week", "get product info",
                 "count units sold", "generate response"}
MAX_STEPS = 6


def planner(task, attempt):
    """MOCK-планировщик. Первый план содержит действие, которого нет в списке tools."""
    if "price of the top product" in task:
        if attempt == 0:
            return ["search the web for prices", "get product info", "generate response"]  # плохой план
        return ["get current date", "find top product of the last week", "get product info", "generate response"]
    return ["count units sold", "generate response"]


def validate_plan(plan):
    problems = [f"нет такого действия: {a!r}" for a in plan if a not in KNOWN_ACTIONS]
    if len(plan) > MAX_STEPS:
        problems.append(f"слишком много шагов: {len(plan)} > {MAX_STEPS}")
    return problems


print("\n== 1. Планирование отделено от выполнения: сначала проверяем план")
task = "What is the price of the top product of the last week?"
for attempt in range(3):
    plan = planner(task, attempt)
    problems = validate_plan(plan)
    print(f"попытка {attempt + 1}: {plan}")
    if not problems:
        print("  план годен, выполняем")
        break
    print("  отклонён:", problems)

# ---------------------------------------------------------------- executor + reflection
print("\n== 2. Выполнение плана: мысль -> действие -> наблюдение (стиль ReAct)")
state = {}


def execute(action):
    """Translator: переводит шаг плана на естественном языке в вызов функции с параметрами из state."""
    if action == "get current date":
        state["today"] = get_today_date()
        return "today", state["today"]
    if action == "find top product of the last week":
        rows = run_sql(text_to_sql("top product", hint="schema"))
        state["top"] = rows[0][0]
        return "run_sql(top product)", rows
    if action == "get product info":
        state["info"] = fetch_product_info(state["top"])
        return f"fetch_product_info({state['top']!r})", state["info"]
    if action == "generate response":
        return "generate_response", f"Цена самого продаваемого товара ({state['top']}) — ${state['info']['price']}"


for i, step in enumerate(plan, 1):
    act, obs = execute(step)
    print(f"Мысль {i}: нужно выполнить шаг «{step}»")
    print(f"Действие {i}: {act}")
    print(f"Наблюдение {i}: {obs}")

print("\n== 3. Reflection: первая попытка SQL падает, агент разбирает ошибку и исправляет запрос")
question = "How many units of Fruity Fedora were sold in the last 7 days?"
hint, evaluator_verdict = None, None
for attempt in range(1, 4):
    sql = text_to_sql(question, hint)
    print(f"Попытка {attempt}. SQL: {sql}")
    try:
        result = run_sql(sql)
        print(f"  результат: {result} -> evaluator: цель достигнута")
        break
    except sqlite3.OperationalError as e:
        print(f"  ошибка выполнения: {e}")
        print("  evaluator: цель не достигнута")
        schema = [r[1] for r in db.execute("PRAGMA table_info(sales)")]
        missing = str(e).split(": ")[-1]
        close = difflib.get_close_matches(missing, schema, n=1, cutoff=0.5)
        print(f"  reflection: колонки {missing!r} нет. Колонки таблицы: {schema}. Ближайшая по написанию: {close}.")
        hint = "use real column names"
print("Без reflection агент остановился бы на первой ошибке или решил бы, что всё хорошо.")

print("\n== 4. Control flow: параллельные шаги снижают latency")
LATENCY_MS = 300  # условное время одного вызова tool
top5 = [r[0] for r in db.execute("SELECT product FROM sales GROUP BY product ORDER BY SUM(units) DESC LIMIT 5")]
print(f"шаг A: найти top-5 товаров -> {top5}")
print(f"шаги B..F: цена каждого из {len(top5)} товаров (независимые вызовы)")
print(f"  последовательно: {len(top5) * LATENCY_MS} мс, параллельно: {LATENCY_MS} мс (по условной задержке {LATENCY_MS} мс на вызов)")
under_15 = [p for p in top5 if PRICES[p] < 15]
print(f"запрос «топ-товары дешевле $15» -> {under_15}")

print("\n== 5. Цикл с условием и ограничение числа шагов")
n, steps = 0, 0
is_prime = lambda x: x > 1 and all(x % d for d in range(2, int(x ** 0.5) + 1))  # noqa: E731
r2 = random.Random(11)
while steps < MAX_STEPS * 5:  # жёсткий предел: агент не должен крутиться бесконечно
    steps += 1
    n = r2.randint(2, 40)
    if is_prime(n):
        break
print(f"генерируем числа, пока не получим простое: нашли {n}, шагов: {steps}")
print(f"предел шагов агента: {MAX_STEPS * 5}. Без предела ошибка планировщика сжигает деньги на API.")

print("\n== 6. Журнал вызовов (его нужно хранить и смотреть при разборе сбоев)")
print(f"всего вызовов tools: {len(CALLS)}")
for name, args, out in CALLS[:4]:
    print(f"  {name}: {str(out)[:60]}")
