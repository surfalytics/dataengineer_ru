# Схемы: Engineering Leadership: The Hard Parts

В книге мало рисунков. Почти все схемы наши.
Исходники: `chNN_diagrams.py`. Запуск: `python3 scripts/engineering-leadership-hard-parts-diagrams/chNN_diagrams.py [name ...]`.
Обзор книги использует `ch11-system.png` как карту книги.

| Глава | Figure | Идея | Наш файл | Статус |
|---|---|---|---|---|
| 2 | Figure 2-1 (+ Table 2-1) | Хаос и симптомы раскладываются на пять опор | ch02-five-pillars.png | redrawn |
| 2 | — (процесс опроса из упражнения) | Цикл Process Pulse Survey | ch02-pulse-loop.png | own |
| 2 | — | Пять упражнений складываются в описание роли | ch02-role-description.png | own |
| 1 | (в книге нет рисунков) | Десять признаков хаоса в трёх группах (наша группировка) | ch01-chaos-symptoms.png | redrawn: own diagram (главная) |
| 1 | (в книге нет рисунков) | Хаос и фатализм подпитывают друг друга (сноска 1 главы) | ch01-fatalism-loop.png | own diagram |
| 1 | (в книге нет рисунков) | Вопросы «остаться или уйти» | ch01-stay-or-leave.png | own diagram |
| 1 | (в книге нет рисунков) | Пять опор роли руководителя | — | skipped: опоры рисует глава 2 (ch02-five-pillars.png), в главе 1 только список |
| 3 | Figure 3-1 | Диапазон и четыре переключателя | ch03-leadership-range.png | redrawn |
| 3 | own | Четыре линзы и действие, которое даёт каждая | ch03-four-lenses.png | own (вместо таблиц 3-1...3-4) |
| 3 | own | Пилот, медик, инженер: когда и риск | ch03-three-roles.png | own |
| 3 | Table 3-1...3-4 | Таблицы по линзам | — | перестроены как таблицы в тексте (среды, сопротивление и выгорание), остальное в тексте |
| 4 | — (в тексте главы рисунков нет) | Четыре шага: безопасность, работоспособность, способности, рост | ch04-path.png | redrawn (наша схема) |
| 4 | — | Пять шагов к работоспособной команде | ch04-functional-steps.png | redrawn (наша схема) |
| 4 | — | Цикл рамки способностей | ch04-capability-loop.png | redrawn (наша схема) |
| 4 | — | Семь способностей сильных команд | ch04-seven-capabilities.png | redrawn (наша схема) |
| 5 | own | Дрейф и направление: две цепочки и ясность между ними | ch05-drift-vs-direction.png | drawn |
| 5 | Figure 5-1 | Цикл выхода из дрейфа в шесть шагов | ch05-drift-recovery.png | redrawn |
| 5 | own | Clarity Workshop: пять шагов с минутами | ch05-clarity-workshop.png | drawn |
| 5 | Table 5-1 | Диагностика дрейфа | таблица на странице (3 колонки из 4) | redrawn as table |
| 7 | Figure 7-1 | Шаблон бюджета инженерной команды (таблица по месяцам, расходы, доход) | — | skipped as a copy: это таблица-шаблон; на странице описана словами, а ход работы с бюджетом нарисован как цикл |
| 7 | Table 7-1 | Вилки зарплат по уровням | — | перестроена в текст |
| 7 | — (наша) | Цикл бюджета из 8 шагов | ch07-budget-cycle.png | drawn |
| 7 | — (наша) | Unit economics: решения инженеров в деньгах | ch07-unit-economics.png | drawn |
| 7 | — (наша) | Полная стоимость сотрудника | ch07-full-cost.png | drawn |
| 7 | — (наша) | Build versus buy | ch07-build-vs-buy.png | drawn |
| 6 | — | Вся цепочка: входы, user stories, матрица, backlog, спринт, пересмотр, коммуникация | ch06-execution-flow.png | own diagram |
| 6 | Figure 6-1 | Шаблон user story с примером про двухфакторную аутентификацию | ch06-user-story.png | redrawn |
| 6 | Figure 6-2 | Четыре квадранта «эффект и усилия» | ch06-impact-effort.png | redrawn |
| 6 | — | Ритм двухнедельного спринта | ch06-sprint-cadence.png | own diagram |
| 8 | Figure 8-1 | Первая схема систем стартапа, которую Джеймс нарисовал в первый день | — | skipped: пример схемы из конкретного стартапа, идеи кроме «нарисуйте инвентарь» нет; идея передана текстом |
| 8 | Figure 8-2 | Mind map вопросов CTO за первые 90 дней (компания, продукт, техника, люди) | — | skipped: список вопросов-чек-лист, пересказан в тексте одним абзацем |
| 8 | own | Пять шагов главы | ch08-strategy-flow.png | redrawn (own) |
| 8 | own | Воркшоп по техническим принципам, 6 шагов | ch08-principles-workshop.png | redrawn (own) |
| 8 | own | Как выбирать технологию: build/buy, скучная технология, жетоны | ch08-tech-choice.png | redrawn (own) |
| 8 | own | Детализация плана по кварталам (пример Эйприл) | ch08-granularity.png | redrawn (own) |
| 9 | (в главе нет рисунков) | Карта главы: принципы, общение/сотрудничество/исполнение, решения, безопасность | ch09-overview.png | own, drawn |
| 9 | — | Multicast против спама | ch09-multicast.png | own, drawn |
| 9 | — | Путь RFC от идеи до ADR | ch09-rfc-adr.png | own, drawn |
| 9 | — | Проверка понимания и работа с несогласием | ch09-disagreement.png | own, drawn |
| 10 | Table 10-1 | Разбор вопроса про CI/CD на компоненты | таблица на странице | rebuilt as table |
| 10 | — | От клиентов и вопроса к метрике и обратной связи | ch10-metric-design.png | own |
| 10 | — | DORA плюс метрики под боль | ch10-dora-context.png | own |
| 10 | — | Закон Гудхарта на примере скорости команды | ch10-goodhart-velocity.png | own |
| 10 | — | Жизненный цикл метрики | ch10-metric-lifecycle.png | own |
| 11 | (в книге нет рисунков) | Пять частей руководства в хаосе как одна система с петлёй обратной связи | ch11-system.png (ch11_diagrams.py) | own, drawn |
| 11 | (нет) | Процесс растёт вместе с командой: выживание, стабилизация, рост | ch11-process-growth.png | own, drawn |
| 11 | (нет) | Цикл внедрения: одна практика за раз, минимум месяц | ch11-one-at-a-time.png | own, drawn |
