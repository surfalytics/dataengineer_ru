# Схемы конспекта Claude AI Bible

В книге почти нет рисунков, поэтому большинство схем наши (`own`): мы рисовали их по тексту главы.
Статус: `own` или `redrawn` — схема на странице; `skipped: причина` — не рисовали или убрали.
Схемы собирает `chNN_diagrams.py` через `excb.py`: `python3 scripts/claude-ai-bible-diagrams/chNN_diagrams.py [name ...]`.

| Глава | Figure | Идея | Наш файл | Статус |
|---|---|---|---|---|
| 0 (обзор) | — | Карта книги: шесть частей и 22 главы | ch00-book-map.png | own (ch00_diagrams.py) |
| 1 | — (в книге нет рисунков) | Путь от сырой модели к продукту | ch01-model-vs-product.png | own |
| 1 | — | RLHF и Constitutional AI | ch01-rlhf-vs-constitutional.png | own |
| 1 | — | Продукты и блоки на одних моделях | ch01-products-map.png | own |
| 2 | — | В главе нет рисунков | — | — |
| 2 | наша | Три уровня семейства: Haiku, Sonnet, Opus, их роли и рост цены | ch02-model-family.png | redrawn (наша, главная схема) |
| 2 | наша | Многоуровневая маршрутизация: Haiku → Sonnet → Opus | ch02-tiered-routing.png | redrawn (наша) |
| 2 | наша | Схема выбора модели и повышение/понижение уровня | ch02-decision.png | redrawn (наша) |
| 3 | — (наша) | Шесть признаков сравнения моделей ведут к вопросу «лучше в чём, для кого, за какую цену» | ch03-compare-dimensions.png | own |
| 3 | — (наша) | Пять шагов проверки за 15 минут | ch03-15-min-eval.png | own |
| 3 | — (наша) | «Черновик, потом критика» и расхождения двух моделей как флаг проверки | ch03-multi-model.png | own |
| 4 | — (в книге нет рисунков) | Лестница планов: запас лимитов и администрирование | ch04-plan-ladder.png | own |
| 4 | — | Подписка на чат или аккаунт API: один вопрос | ch04-subscription-vs-api.png | own |
| 4 | — | Оценка расходов на API и лимит расходов | ch04-api-cost-estimate.png | own |
| 5 | — (наша) | Пять частей сильного prompt | ch05-five-ingredients.png | own |
| 5 | — (наша) | Тест постоянного приказа и тест на перегруз | ch05-standing-order.png | own |
| 5 | — (наша) | System prompt над несколькими user prompt | ch05-system-vs-user.png | own |
| 5 | — (наша) | Итерации по одной правке и библиотека prompt | ch05-iteration-loop.png | own |
| 6 | — (наша) | Модель и глубину рассуждения выбирают по сложности задачи | ch06-match-difficulty.png | redrawn (наша, главная) |
| 6 | — (наша) | Проверка JSON на своей стороне и короткий цикл исправления | ch06-json-loop.png | redrawn (наша) |
| 6 | — (наша) | `prompt chaining` с контрольными точками | ch06-prompt-chain.png | redrawn (наша) |
| 7 | — (наша) | Проект как контейнер: инструкции и база знаний входят в каждый разговор | ch07-project-container.png | redrawn (own) |
| 7 | — (наша) | Тест: класть ли документ в базу знаний | ch07-kb-filter.png | redrawn (own) |
| 7 | — (наша) | Три слоя: custom instructions, память, проект | ch07-three-layers.png | redrawn (own) |
| 8 | — (своя) | Чат или artifact: кто решает, правки на месте, экспорт | ch08-chat-or-artifact.png | own |
| 8 | — (своя) | Цикл «собрать, проверить, исправить» на калькуляторе чаевых | ch08-build-test-fix.png | own |
| 8 | — (своя) | Длинный текст по шагам против одного запроса | ch08-staged-writing.png | own |
| 8 | — (своя) | Песочница: что работает и что недоступно | ch08-sandbox-limits.png | own |
| 9 | — (наша) | Один мозг, несколько дверей: 4 входа → аккаунт → 3 модели | ch09-one-brain-doors.png | redrawn (own) |
| 9 | — (наша) | Задача → поверхность (голос и итоговая настройка) | ch09-surface-choice.png | redrawn (own) |
| 9 | — (наша) | Что синхронизируется, а что остаётся на устройстве | ch09-sync-split.png | redrawn (own) |
| 10 | — (в главе нет рисунков) | Границы Cowork: подключённая папка, sandbox shell, MCP connector, подтверждение действий | ch10-cowork-boundaries.png | own (main) |
| 10 | — | Задача по расписанию, коннекторы и live artifact | ch10-scheduled-flow.png | own |
| 10 | — | Три уровня безопасности computer use | ch10-computer-use-tiers.png | own |
| 11 | — | Режим боковой панели и `agentic`-режим: кто ведёт и где риск | ch11-modes.png | own (главная) |
| 11 | — | Многошаговая задача: цикл по каталогу компаний и точки сбоя | ch11-loop.png | own |
| 11 | — | Модель безопасности: текст страницы как данные, запрос на подтверждение, blast radius | ch11-safety.png | own |
| 11 | — | Какую поверхность выбрать для веб-задачи | ch11-surface.png | own |
| 12 | — (в главе нет рисунков) | Разделение труда: агент делает механику, человек даёт бриф, решает по пометкам и проверяет | ch12-division-of-labor.png | own |
| 12 | — | Порядок проверки цифр: порядок величины, трассировка, смена входа, сверка | ch12-verification.png | own |
| 12 | — | Excel как звено цепочки: источник, коннектор, Excel + Claude, Cowork, сводка | ch12-workflow-chain.png | own |
| 13 | — (в книге нет рисунков) | Цикл explore, plan, edit, run, iterate с одобрением плана | ch13-agent-loop.png | redrawn: своя схема по тексту, главная |
| 13 | — | Главный агент раздаёт задачи subagent и собирает сводки | ch13-subagents.png | redrawn: своя схема по тексту |
| 13 | — | События hooks: SessionStart, PreToolUse (запрет), PostToolUse, Stop | ch13-hooks.png | redrawn: своя схема по тексту |
| 13 | — | Git как кнопка «отменить»: status, задача, diff, commit или откат | ch13-git-safety.png | redrawn: своя схема по тексту |
| 14 | — (в книге нет рисунков) | Как Claude выбирает skill и грузит его слоями | ch14-skill-loading.png | own (главная схема) |
| 14 | дерево папки weekly-store-summary/ (текстом) | Из чего состоит папка skill | ch14-skill-folder.png | redrawn |
| 14 | — | Две проверки skill и где править | ch14-testing-loop.png | own |
| 14 | — | Когда skill нужен, а когда MCP server, CLAUDE.md или обычный вопрос | ch14-when-skill.png | own |
| 15 | — (в книге нет рисунков) | Что внутри plugin release-notes-kit: manifest и четыре части | ch15-plugin-bundle.png | own |
| 15 | — | Путь plugin: автор, внутренний marketplace, установка для себя и на уровне проекта, обновление | ch15-marketplace-flow.png | own |
| 15 | — | Проверка до установки в 4 шага и цикл порядка для команды | ch15-vetting.png | own |
| 15 | дерево папок release-notes-kit (текст) | Структура plugin | вывод ch15_plugin_check.py | redrawn как вывод скрипта |
| 16 | — (в книге рисунков нет) | «инструменты × продукты» против «инструменты + продукты» | ch16-n-times-m.png | own |
| 16 | — | `host`, `client`, `server`, внешние системы, `tools`/`resources`/`prompts`, `stdio` и HTTP | ch16-architecture.png | own (главная) |
| 16 | — | `confused deputy` из истории про Мельбурн и слои защиты | ch16-confused-deputy.png | own |
| 17 | — | Устройство запроса к Messages API и петля истории (`stateless`) | ch17-request-anatomy.png | own (главная) |
| 17 | — | Когда брать чат-приложение, а когда API | ch17-api-or-chat.png | own |
| 17 | — | `Prompt caching`: стабильное начало в кэше, новое в конце | ch17-caching.png | own |
| 17 | — | Что делать с успехом, временной ошибкой и ошибкой запроса | ch17-errors.png | own |
| 18 | текстовый набросок «loop the SDK runs for you» | Цикл агента: решение, инструмент, результат, повтор; лимит как стоп | ch18-agent-loop.png | redrawn (главная) |
| 18 | — (рисунка нет) | Четыре слоя guardrails: инструменты, одобрение, песочница, лимиты | ch18-guardrails.png | own |
| 18 | текстовый набросок «orchestration» | Оркестратор, три subagent (безопасность, скорость, стиль), сбор итога | — | skipped: та же идея, что ch13-subagents.png; в главе 18 ссылка на главу 13 |
| 19 | — (в книге рисунков нет) | Цикл `tool use`: `tools`, `tool_use`, ваш код, `tool_result` | ch19-round-trip.png | own (главная) |
| 19 | — | Исправимая ошибка с `is_error` против остановки цикла | ch19-tool-errors.png | own |
| 19 | — | Есть API — `tool use`, нет — `computer use` с песочницей и человеком | ch19-api-or-screen.png | own |
| 19 | — | Счёт: зрение, сверка суммы, `check_purchase_order`, `flag_for_review` | ch19-invoice-flow.png | own |
| 20 | — (наша) | Один вызов, workflow или агент: каждый слой сложности надо заслужить | ch20-complexity-ladder.png | redrawn (наша, главная) |
| 20 | — (наша) | Автоматизация поддержки из нескольких паттернов (OPERATOR'S EDGE и план запуска) | ch20-support-patterns.png | redrawn (наша) |
| 20 | — (наша) | Возвраты денег до и после сужения `blast radius` (FROM THE TRENCHES) | ch20-blast-radius.png | redrawn (наша) |
| 20 | — (наша) | Семь шагов запуска одной автоматизации | ch20-shipping-arc.png | redrawn (наша) |
| 21 | — (в книге рисунков нет) | общая форма 12 кейсов: агент делает черновик по своим материалам, помечает неуверенность, человек решает | ch21-common-shape.png | own (главная) |
| 21 | — | проверку только требуют против проверки, сделанной дешёвой (цитата у юристов) | ch21-cheap-verification.png | own |
| 21 | — | рецепт из пяти шагов «копируйте форму, а не инструмент» | ch21-five-steps.png | own |
| 22 | — (в книге рисунков нет) | Пять ограничений модели и чем их закрывает человек | ch22-four-limits.png | own (главная) |
| 22 | — | Откуда берётся галлюцинация и приёмы защиты | ch22-hallucination.png | own |
| 22 | — | Уровни автоматизации: автоматически или человек, плюс выборочная проверка | ch22-tiering.png | own |
