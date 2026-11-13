"""Глава 5: разбиение задачи на цепочку prompts (prompt chaining) на примере бота поддержки.
Модели здесь ненастоящие: classify_intent() работает по ключевым словам, write_reply() выдаёт шаблонный ответ.
В настоящей системе это два вызова API: дешёвая модель классифицирует, сильная пишет ответ.
Цены и скорость условные (обозначены в PRICE и SPEED), подставьте свои.
Что показывает:
 1. цепочку: тип запроса -> prompt под этот тип -> ответ, и журнал промежуточных результатов (мониторинг);
 2. отладку: первый шаг проверяем отдельно на своём наборе, второй шаг не трогаем;
 3. цену и задержку: один большой prompt против цепочки;
 4. параллельность: независимые шаги идут одновременно (считаем время, настоящих потоков нет).
Запуск: python3 -I scripts/ai-engineering-code/ch05_prompt_chain.py   (только стандартная библиотека)"""
import json
import re


def count_tokens(text):
    """Грубая оценка числа токенов: слово или группа знаков препинания."""
    return len(re.findall(r"\w+|[^\w\s]+", text))


# --- Шаг 1: определить тип запроса -----------------------------------------------------------
RULES = [  # (primary, secondary, ключевые слова)
    ("billing", "refund", ["возврат", "верните", "вернуть деньги"]),
    ("billing", "invoice", ["счёт", "счет", "оплат"]),
    ("tech", "troubleshooting", ["интернет", "роутер", "не работает", "ошибка"]),
    ("account", "password", ["пароль", "не могу войти"]),
    ("account", "delete", ["удалить аккаунт"]),
]
CLASSIFY_PROMPT = ("Определи тип запроса клиента. Верни JSON с ключами primary и secondary.\n"
                   "primary: billing, tech, account или other.")


def classify_intent(query):
    q = query.lower()
    for primary, secondary, words in RULES:
        if any(w in q for w in words):
            return json.dumps({"primary": primary, "secondary": secondary})
    return json.dumps({"primary": "other", "secondary": "general"})


# --- Шаг 2: prompt под тип запроса ------------------------------------------------------------
INTENT_PROMPTS = {
    "billing": "Ты оператор по оплатам. Попроси номер заказа. Возврат идёт 5 рабочих дней. Деньги возвращаем на ту же карту.",
    "tech": "Ты оператор техподдержки. Попроси проверить кабели и перезагрузить роутер. Если не помогло, позови инженера.",
    "account": "Ты оператор по аккаунтам. Не проси пароль. Дай ссылку на сброс пароля. Удаление аккаунта подтверждай по почте.",
    "other": "Ты оператор. Вежливо уточни, чем можно помочь.",
}
REPLIES = {
    "billing": "Пришлите номер заказа. Возврат займёт 5 рабочих дней.",
    "tech": "Проверьте, что все кабели роутера подключены, и перезагрузите его.",
    "account": "Откройте страницу сброса пароля. Письмо придёт на вашу почту.",
    "other": "Расскажите подробнее, чем помочь?",
}


def write_reply(system_prompt, query, primary):
    return REPLIES[primary]  # настоящая модель написала бы ответ по system_prompt и запросу


def run_chain(query, log):
    intent_raw = classify_intent(query)
    log.append(("шаг 1: тип запроса", query, intent_raw))
    primary = json.loads(intent_raw)["primary"]
    reply = write_reply(INTENT_PROMPTS[primary], query, primary)
    log.append((f"шаг 2: prompt для «{primary}»", query, reply))
    return reply


# --- Один большой prompt для всего сразу -------------------------------------------------------
EDGE = ["Если клиент злится, сначала извинись.", "Не обещай сроки, которых нет в правилах.",
        "Не называй внутренние названия систем.", "Если вопрос про цену, отправь на страницу тарифов.",
        "Если клиент пишет на другом языке, отвечай на нём.", "Не проси номер карты целиком."]
BIG_PROMPT = ("Ты оператор поддержки. Определи тип запроса и ответь по правилам своего типа.\n"
              + "\n".join(f"Тип {k}: {v}" for k, v in INTENT_PROMPTS.items())
              + "\nОбщие правила:\n" + "\n".join(EDGE * 4))

# --- Условные цены (доллары за 1 млн токенов) и скорость ----------------------------------------
PRICE = {"strong": (3.00, 15.00), "cheap": (0.25, 1.00)}   # (вход, выход)
SPEED = {"strong": (0.50, 0.020), "cheap": (0.20, 0.010)}  # (время до первого токена, сек/токен вывода)


def call_cost(model, tokens_in, tokens_out):
    p_in, p_out = PRICE[model]
    return (tokens_in * p_in + tokens_out * p_out) / 1_000_000


def call_time(model, tokens_out):
    ttft, per_token = SPEED[model]
    return ttft + tokens_out * per_token


QUERIES = ["Хочу вернуть деньги за заказ 4512", "Не работает интернет, роутер мигает красным",
           "Забыл пароль, не могу войти", "Можно ли оплатить счёт с карты друга?",
           "Привет, как у вас дела?", "Хочу удалить аккаунт и вернуть деньги"]

print("== 1. Цепочка и журнал промежуточных результатов")
for q in QUERIES[:3]:
    log = []
    reply = run_chain(q, log)
    for step, inp, out in log:
        print(f"  {step}: {out}")
    print(f"  запрос: {q!r} -> ответ: {reply!r}\n")

print("== 2. Отладка: проверяем только шаг 1 на размеченных запросах")
LABELED = [("Верните мне деньги", "billing"), ("Где мой счёт?", "billing"), ("Роутер не работает", "tech"),
           ("Ошибка при входе в кабинет", "tech"), ("Не могу войти", "account"),
           ("Хочу удалить аккаунт", "account"), ("Сколько стоит тариф?", "other"),
           ("Хочу удалить аккаунт и вернуть деньги", "account")]
wrong = [(q, want, json.loads(classify_intent(q))["primary"]) for q, want in LABELED
         if json.loads(classify_intent(q))["primary"] != want]
print(f"точность шага 1: {len(LABELED) - len(wrong)}/{len(LABELED)}")
for q, want, got in wrong:
    print(f"  ошибка: {q!r}: ждали {want}, получили {got}")
print("Чиним правила шага 1. Шаг 2 и его prompts не меняются.")

print("\n== 3. Цена и задержка: один большой prompt против цепочки (условные цены)")
avg_q = sum(count_tokens(q) for q in QUERIES) / len(QUERIES)
reply_tokens = sum(count_tokens(r) for r in REPLIES.values()) / len(REPLIES)
big_in = count_tokens(BIG_PROMPT) + avg_q
a_cost = call_cost("strong", big_in, reply_tokens)
a_time = call_time("strong", reply_tokens)
cls_in = count_tokens(CLASSIFY_PROMPT) + avg_q
cls_out = 12  # токенов в JSON с типом запроса
step2_in = sum(count_tokens(p) for p in INTENT_PROMPTS.values()) / len(INTENT_PROMPTS) + avg_q
b_cost = call_cost("cheap", cls_in, cls_out) + call_cost("strong", step2_in, reply_tokens)
b_time = call_time("cheap", cls_out) + call_time("strong", reply_tokens)
b_first = call_time("cheap", cls_out) + SPEED["strong"][0]
print(f"большой prompt: {count_tokens(BIG_PROMPT)} токенов (в игрушечном примере, у GoDaddy было больше 1500)")
print("вариант                 | токенов на входе | цена за запрос | время до ответа | до первого токена")
print(f"A. один большой prompt  | {big_in:16.0f} | ${a_cost:.6f}    | {a_time:6.2f} с         | {SPEED['strong'][0]:.2f} с")
print(f"B. цепочка из 2 шагов   | {cls_in + step2_in:16.0f} | ${b_cost:.6f}    | {b_time:6.2f} с         | {b_first:.2f} с")
def money(x):
    return f"${x:,.0f}".replace(",", " ")


print(f"цена на 1 млн запросов: A = {money(a_cost * 1e6)}; B = {money(b_cost * 1e6)}")

print("\n== 4. Параллельность: три независимых шага (история для трёх уровней чтения)")
out_tokens = 120
one = call_time("strong", out_tokens)
print(f"один шаг: {one:.2f} с; три шага подряд: {3 * one:.2f} с; три шага параллельно: {one:.2f} с")
print("Цена та же. Время сократилось втрое, потому что шаги не зависят друг от друга.")
