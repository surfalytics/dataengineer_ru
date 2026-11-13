"""Глава 9: от throughput к деньгам. Калькулятор цены inference.
Числа взяты из примеров главы: сервер за $2 в час, 100 токенов в секунду, 100 запросов prefill в минуту.
Цена токена в блоке про prompt caching придумана нами: подставьте цены вашего провайдера.
Запуск: python3 scripts/ai-engineering-code/ch09_cost_calculator.py   (только стандартная библиотека)"""

HOUR = 3600

print("== 1. Цена decode: throughput -> доллары за токен")
usd_per_hour = 2.0
decode_tps = 100            # токенов в секунду по всему серверу
out_per_request = 200       # выходных токенов на запрос
per_1m_out = usd_per_hour / (decode_tps * HOUR) * 1_000_000
decode_1k = per_1m_out * out_per_request * 1000 / 1_000_000
print(f"${usd_per_hour}/ч и {decode_tps} токенов/с -> ${per_1m_out:.3f} за 1 млн выходных токенов")
print(f"1000 запросов по {out_per_request} токенов: ${decode_1k:.2f} на decode")

print("\n== 2. Цена prefill и итог на 1000 запросов")
prefill_rpm = 100           # запросов в минуту на prefill
prefill_1k = usd_per_hour / (prefill_rpm * 60) * 1000
print(f"prefill {prefill_rpm} запросов/мин -> ${prefill_1k:.2f} за 1000 запросов")
total_1k = decode_1k + prefill_1k
print(f"итого на 1000 запросов: ${decode_1k:.2f} + ${prefill_1k:.2f} = ${total_1k:.2f}")

print("\n== 3. Что даёт рост throughput и batch API")
for k in (1, 2, 3):
    print(f"throughput x{k}: ${per_1m_out / k:.3f} за 1 млн выходных токенов")
print(f"batch API со скидкой 50%: ${total_1k:.2f} -> ${total_1k * 0.5:.2f} на 1000 запросов (цена: ответ придёт через часы)")

print("\n== 4. Выходной токен тяжелее входного (оценка Anyscale: 1 выходной токен ~ 100 входных по влиянию на latency)")
for in_tok, out_tok in [(1000, 200), (10_000, 200), (500, 1500)]:
    in_equiv = in_tok / 100
    share = out_tok / (out_tok + in_equiv)
    print(f"вход {in_tok:>6}, выход {out_tok:>5}: вход весит как {in_equiv:>5.0f} выходных токенов, на выход приходится {share:.1%} latency")

print("\n== 5. Prompt caching: что даёт стабильное начало prompt")
prompt_tokens = 1000
calls_per_day = 1_000_000
saved = prompt_tokens * calls_per_day
print(f"{prompt_tokens} токенов prompt x {calls_per_day:,} вызовов = {saved:,} повторяющихся входных токенов в день".replace(",", " "))
price_in = 1.00             # наша цена: $ за 1 млн входных токенов (подставьте свою)
discount = 0.75             # скидка на cached токены (как у Gemini в книге)
storage = 1.00              # плата за хранение кэша: $ за 1 млн токенов в час (как у Gemini в книге)
no_cache = saved / 1e6 * price_in
with_cache = saved / 1e6 * price_in * (1 - discount) + prompt_tokens / 1e6 * storage * 24
print(f"без кэша: ${no_cache:,.0f} в день; с кэшем: ${with_cache:,.2f} в день; экономия ${no_cache - with_cache:,.2f}".replace(",", " "))

print("\nСнижение latency по трём сценариям Anthropic (значения из таблицы книги):")
for name, before, after in [("чат с книгой, 100 000 токенов", 11.5, 2.4),
                            ("prompt с примерами, 10 000 токенов", 1.6, 1.1),
                            ("диалог из 10 реплик", 10.0, 2.5)]:
    print(f"{name:<38} TTFT {before:>4} с -> {after:>3} с ({after / before - 1:+.0%})")
