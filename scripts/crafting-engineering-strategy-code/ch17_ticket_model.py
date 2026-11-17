#!/usr/bin/env python3
"""Модель пути тикета (Document 17-2, глава 17): формулы таблицы переписаны на Python, без зависимостей.
Запуск: python3 -I ch17_ticket_model.py
Пять накопителей: открытые -> в работе -> протестированы -> задеплоены -> закрыты.
Три обратных потока: ошибка в тесте, ошибка при деплое, ошибка в проде. Печатает закрытые тикеты по раундам."""
from math import floor


def run(rounds=30, open_rate=1, start_rate=1, test_rate=1, max_started=3,
        err_test=0.1, err_deploy=0.1, err_prod=0.25):
    opened, started, tested, deployed, closed = 1, 0, 0, 0, 0   # первая строка: литералы
    hist = []
    for _ in range(rounds):
        to_start = 0 if started >= max_started else start_rate  # StartCodingMore?
        to_start = min(to_start, opened + open_rate)
        to_test = min(test_rate, started)                       # NumToTest?
        to_deploy = tested                                      # все протестированное уходит в деплой
        to_close = deployed                                     # все задеплоенное закрывается
        e_test = floor(tested * err_test)                       # ErrorsFoundInTest?
        e_deploy = floor(deployed * err_deploy)                 # ErrorsFoundInDeploy?
        e_prod = floor(closed * err_prod)                       # ErrorsFoundInProd?
        opened += open_rate - to_start + e_prod
        started += to_start - to_test + e_test + e_deploy
        tested += to_test - to_deploy - e_test
        deployed += to_deploy - to_close - e_deploy
        closed += to_close - e_prod
        hist.append(closed)
    return hist


SCENARIOS = [
    ("1. База (ошибок в проде 25%)", {}),
    ("2. Ошибок в проде 10%", dict(err_prod=0.10)),
    ("3. Тестируем втрое быстрее", dict(test_rate=3)),
    ("4. Тестируем и начинаем втрое быстрее", dict(test_rate=3, start_rate=3)),
]

print(f"{'Сценарий':<42}{'раунд 10':>9}{'раунд 30':>9}{'раунд 100':>10}")
for name, kw in SCENARIOS:
    h = run(rounds=100, **kw)
    print(f"{name:<42}{h[9]:>9}{h[29]:>9}{h[99]:>10}")
