"""Глава 5: считаем цену prompt. Few-shot примеры, повтор system prompt, длинный контекст, скрытые вызовы инструментов.
Все цены условные (PRICE): подставьте цены своей модели. Токены считаем заданными числами, без токенизатора.
Что показывает:
 1. сколько стоят few-shot примеры при миллионе запросов в месяц;
 2. сколько добавляет повтор system prompt (защитный приём);
 3. сколько стоит один запрос с заполненным длинным контекстом;
 4. сколько вызовов API делает инструмент автоподбора prompt и во сколько это обойдётся.
Запуск: python3 -I scripts/ai-engineering-code/ch05_cost_estimate.py   (только стандартная библиотека)"""

PRICE_IN, PRICE_OUT = 3.00, 15.00  # доллары за 1 млн токенов, условные


def cost(tokens_in, tokens_out, calls=1):
    return calls * (tokens_in * PRICE_IN + tokens_out * PRICE_OUT) / 1_000_000


def money(x, digits=0):
    return f"${x:,.{digits}f}".replace(",", " ")


print(f"Условные цены: вход ${PRICE_IN:.2f} за 1 млн токенов, выход ${PRICE_OUT:.2f} за 1 млн токенов.")

print("\n== 1. Few-shot: каждый пример это токены на каждом запросе")
BASE, PER_SHOT, OUT = 120, 25, 20  # описание задачи + сам вопрос / один пример / ответ
REQUESTS = 1_000_000
print("примеров | токенов на входе | цена запроса | цена за 1 млн запросов")
for n in (0, 1, 3, 5, 10, 20):
    t_in = BASE + n * PER_SHOT
    print(f"{n:>8} | {t_in:>16} | {money(cost(t_in, OUT), 6):>12} | {money(cost(t_in, OUT) * REQUESTS):>10}")
print(f"20 примеров делают запрос дороже в {cost(BASE + 20 * PER_SHOT, OUT) / cost(BASE, OUT):.1f} раза по сравнению с zero-shot: платим за токены входа.")

print("\n== 2. Повтор system prompt до и после ввода пользователя")
SYSTEM, USER, REPLY = 400, 200, 150
one = cost(SYSTEM + USER, REPLY)
two = cost(2 * SYSTEM + USER, REPLY)
print(f"один раз: {SYSTEM + USER} токенов входа, {money(one * REQUESTS)} за 1 млн запросов")
print(f"дважды:   {2 * SYSTEM + USER} токенов входа, {money(two * REQUESTS)} за 1 млн запросов")
print(f"надбавка: +{two / one - 1:.0%} к цене и +{SYSTEM / (SYSTEM + USER):.0%} к длине входа, то есть и к времени обработки prompt.")

print("\n== 3. Длинный контекст: сколько книг влезает и сколько стоит заполнить")
TOKENS_PER_WORD = 160_000 / 120_000  # у книги из главы: около 120 тысяч слов и 160 тысяч токенов
BOOK = 160_000
print("контекст    | книг по 160 тыс. токенов | слов (примерно) | цена одного запроса на полном контексте")
for name, ctx in (("1K", 1_000), ("100K", 100_000), ("1M", 1_000_000), ("2M", 2_000_000)):
    words = ctx / TOKENS_PER_WORD
    print(f"{name:<11} | {ctx / BOOK:>24.2f} | {words:>15,.0f} | {money(cost(ctx, 500), 2)}".replace(",", " "))
print("Полный контекст 2M при каждом запросе стоит несколько долларов. Поэтому длинный prompt нужно сокращать.")

print("\n== 4. Скрытые вызовы инструмента автоподбора prompt")
VARIANTS, EVAL_EXAMPLES = 10, 30
steps = {"сгенерировать ответ": 1, "проверить формат (JSON валиден?)": 1, "оценить ответ судьёй": 1}
per_example = sum(steps.values())
base_calls = VARIANTS * EVAL_EXAMPLES
total_calls = base_calls * per_example
print(f"вариантов prompt: {VARIANTS}, примеров в eval-наборе: {EVAL_EXAMPLES}")
print(f"если считать 1 вызов на пару: {base_calls} вызовов")
print(f"на самом деле на пару приходится {per_example} вызова ({', '.join(steps)}): {total_calls} вызовов")
AVG_IN, AVG_OUT = 500, 100
print(f"при {AVG_IN} токенов входа и {AVG_OUT} выхода один прогон стоит {money(cost(AVG_IN, AVG_OUT, total_calls), 2)}")
rounds = 5
print(f"если инструмент делает {rounds} раундов и каждый раунд меняет {VARIANTS} вариантов: "
      f"{total_calls * rounds} вызовов, {money(cost(AVG_IN, AVG_OUT, total_calls * rounds), 2)}")
LIMIT = 1000
print(f"\nЗащита от сюрприза: ставим лимит {LIMIT} вызовов и останавливаемся заранее.")
calls = 0
for r in range(1, rounds + 1):
    if calls + total_calls > LIMIT:
        print(f"раунд {r}: лимит {LIMIT} был бы превышен ({calls + total_calls} вызовов), остановка")
        break
    calls += total_calls
    print(f"раунд {r}: выполнено {calls} вызовов")
