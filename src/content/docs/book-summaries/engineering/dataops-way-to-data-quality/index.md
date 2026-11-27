---
title: "The DataOps Way to Data Quality and Data Observability — конспект книги"
head:
  - tag: title
    content: "DataOps: качество и наблюдаемость данных | Инжиниринг Данных"
description: "Конспект 63 глав книги DataKitchen о качестве и наблюдаемости данных. Проверки, мониторинг, организационные решения, кейсы и практические примеры."
author: "Christopher Bergh, Charles Bloche, Gil Benghiat"
sidebar:
  order: 0
  label: "Обзор книги"
tags:
  - books
  - dataops
  - data-quality
---

**The DataOps Way to Data Quality and Data Observability. A Practitioner's Guide to Building Data Teams That Deliver** написали Christopher Bergh, Charles Bloche и Gil Benghiat. Издатель — DataKitchen, Inc., первое издание 2026 года, редакция от 23 сентября. В книге 63 статьи в семи разделах. Авторы разбирают, как команде обнаруживать ошибки до публикации данных и проверять, что изменение в конвейере не испортило уже работающий расчёт.

> Это подробный пересказ на русском, а не перевод. Полный текст доступен на [сайте издателя](https://datakitchen.io/books/the-dataops-way-to-data-quality-a-free-book-for-every-data-team/).

📥 [Скачать конспект в EPUB](/downloads/dataops-way-to-data-quality.epub) для телефона или электронной книги.

![Карта семи разделов книги о качестве и наблюдаемости данных](/assets/dataops-way-to-data-quality/ch00-book-map.png)

## О чём книга простыми словами

К восьми утра должен появиться отчёт о выручке. Все задачи оркестратора завершились успешно. Позже выясняется, что один поставщик передал половину строк, а курс валюты в соседней таблице остался вчерашним. Из одного статуса «успешно» команда не узнает, можно ли использовать цифру. Нужны проверки на этапах получения и преобразования, сведения о конкретном запуске и договорённость, какой результат позволяет выпускать отчёт.

Авторы связывают надёжность с двумя видами работы. Во время поставки команда проверяет пришедшие данные, сверяет результаты и останавливает ошибочную партию. Во время разработки она прогоняет новый код на известных входах и сравнивает результат с ожидаемым. Ответственность за правило и реакцию на него распределяют до инцидента. Иначе один инженер знает, что число невозможно, другой видит красный сигнал, а руководитель узнаёт обо всём от пользователя.

DataKitchen разрабатывает TestGen и DataOps Observability. Когда авторы показывают свои инструменты, приводят клиентскую оценку или сравнивают поставщиков, в главах указано, кому принадлежит вывод.

## Что нужно знать заранее

- Что представляет одна строка таблицы, как связаны первичный и внешний ключи и как соединение может размножить записи.
- Как сырые данные проходят загрузку, преобразование и публикацию в витрине.
- Чем ожидание пользователя по времени поставки отличается от технического статуса задачи. Основные понятия можно освежить по конспекту [Data Quality Fundamentals](/book-summaries/engineering/data-quality-fundamentals/).

## Зачем читать

- Выбрать место проверки так, чтобы не разносить ошибку по зависимым таблицам.
- Посчитать, сколько времени команда теряет на исправления и когда новые тесты окупятся.
- Превратить знание аналитика о допустимом значении в правило с владельцем.
- При разборе сбоя связать показатели качества, историю выполнения и сроки потребителей.
- Выбрать инструменты под конкретную операцию и проверить утверждения поставщика на собственных данных.

## Как устроена книга

| Раздел | Главы | Что меняется для команды |
|---|---|---|
| Почему важно качество | 1–10 | Команда оценивает последствия ошибок, цену их исправления и неудобных данных. |
| Культура и организация | 11–20 | У правил появляются владельцы, а разборы перестают сводиться к поиску виноватого. |
| Стратегия тестирования | 21–33 | Проверки распределяются между этапами обработки и этапами разработки. |
| Мониторинг и наблюдаемость | 34–38 | Появляются сигналы для конкретных ролей и решения об остановке процесса. |
| Внедрение и кейсы | 39–46 | Реальные сбои показывают пределы универсальных правил. |
| ИИ и качество | 47–54 | Отдельно проверяются входы для модели и написанные с её помощью преобразования. |
| Инструменты и старт внедрения | 55–63 | Средства сопоставляют с этапами работы и собирают первый план внедрения. |

Первые два раздела помогают выбрать проблему и владельца. Средние разделы показывают механизм проверки и реакции на сбой. Последние помогают оценить, как он работает в отраслевой задаче и на конкретной платформе.

## Главные идеи

| Идея | Где искать |
|---|---|
| Данные и изменение кода проходят разные пути к потребителю. | [Глава 1](/book-summaries/engineering/dataops-way-to-data-quality/01-data-quality-testing-is-at-the-core-of-four-critical-data-team-processes/) и [Глава 21](/book-summaries/engineering/dataops-way-to-data-quality/21-shift-left-shift-down-how-to-take-control-of-data-quality/) |
| У каждой проверки есть стоимость. Важна цена ошибки, которую она способна остановить. | [Глава 6](/book-summaries/engineering/dataops-way-to-data-quality/06-the-economics-of-data-quality-when-to-test-how-much-to-spend/) и [Глава 41](/book-summaries/engineering/dataops-way-to-data-quality/41-when-not-to-test-setting-reasonable-bounds-on-data-quality-effort/) |
| Рабочие правила могут жить только в голове эксперта. Их приходится искать и формулировать. | [Глава 18](/book-summaries/engineering/dataops-way-to-data-quality/18-process-guardianship-the-most-valuable-work-you-are-probably-not-doing/) и [Глава 29](/book-summaries/engineering/dataops-way-to-data-quality/29-your-best-data-quality-rules-live-in-someone-elses-head/) |
| Граф зависимостей указывает затронутые объекты, а содержимое проверяется исполнением. | [Глава 30](/book-summaries/engineering/dataops-way-to-data-quality/30-the-blueprint-or-the-fire-alarm-panel-why-data-test-coverage-beats-data-lineage/) и [Глава 38](/book-summaries/engineering/dataops-way-to-data-quality/38-data-production-tripwires-in-databricks-stop-bad-data-before-it-reaches-production/) |
| Статистически привычное значение иногда невозможно по смыслу. | [Глава 42](/book-summaries/engineering/dataops-way-to-data-quality/42-i-wrote-data-quality-tests-for-3-million-nyc-taxi-rides-in-five-minutes/) и [Глава 46](/book-summaries/engineering/dataops-way-to-data-quality/46-the-illusion-of-clean-data-the-pharma-identifiers-generic-tools-never-check/) |
| Аналитическому агенту требуются актуальные определения, факты запусков и независимая проверка. | [Глава 50](/book-summaries/engineering/dataops-way-to-data-quality/50-context-as-infrastructure-the-six-category-framework-for-ai-ready-data-analysis/) и [Глава 54](/book-summaries/engineering/dataops-way-to-data-quality/54-the-seven-deadly-sins-of-ai-generated-data-pipelines/) |

## Как читать

- **Первое знакомство.** Начните с введения, затем прочтите [главы 1](/book-summaries/engineering/dataops-way-to-data-quality/01-data-quality-testing-is-at-the-core-of-four-critical-data-team-processes/) и [5](/book-summaries/engineering/dataops-way-to-data-quality/05-how-i-broke-our-sla-and-delighted-our-customer/). Историю конкретного сбоя разберите в [главе 40](/book-summaries/engineering/dataops-way-to-data-quality/40-three-data-quality-disasters-and-how-they-were-averted/).
- **Analytics engineer.** В [главах 18](/book-summaries/engineering/dataops-way-to-data-quality/18-process-guardianship-the-most-valuable-work-you-are-probably-not-doing/) и [29](/book-summaries/engineering/dataops-way-to-data-quality/29-your-best-data-quality-rules-live-in-someone-elses-head/) разбирается работа с владельцами показателей. В [главах 25](/book-summaries/engineering/dataops-way-to-data-quality/25-building-data-quality-into-dbt-a-complete-guide/) и [30](/book-summaries/engineering/dataops-way-to-data-quality/30-the-blueprint-or-the-fire-alarm-panel-why-data-test-coverage-beats-data-lineage/) видно, как обнаруживать регрессии, которых нет на графе зависимостей.
- **Инженер данных.** Проследите путь партии в [главе 23](/book-summaries/engineering/dataops-way-to-data-quality/23-data-quality-test-coverage-in-a-medallion-data-architecture/), [главе 32](/book-summaries/engineering/dataops-way-to-data-quality/32-the-four-points-in-your-medallion-architecture-where-data-testing-really-matters/) и [главе 38](/book-summaries/engineering/dataops-way-to-data-quality/38-data-production-tripwires-in-databricks-stop-bad-data-before-it-reaches-production/). Затем сравните две поставки на примере [главы 45](/book-summaries/engineering/dataops-way-to-data-quality/45-iqvia-specialty-pharmacy-and-your-own-files-the-commercial-data-most-likely-to-be-wrong/).
- **Руководитель.** В [главах 4](/book-summaries/engineering/dataops-way-to-data-quality/04-stop-paying-the-data-quality-tax/), [6](/book-summaries/engineering/dataops-way-to-data-quality/06-the-economics-of-data-quality-when-to-test-how-much-to-spend/) и [19](/book-summaries/engineering/dataops-way-to-data-quality/19-how-data-quality-leaders-can-gain-influence-and-avoid-the-tragedy-of-the-commons/) обсуждаются стоимость повторяющейся работы и распределение ответственности. [Главы 55](/book-summaries/engineering/dataops-way-to-data-quality/55-a-practical-guide-to-selecting-data-quality-tools/) и [63](/book-summaries/engineering/dataops-way-to-data-quality/63-where-to-actually-start-with-dataops-in-2026/) помогают перейти к выбору инструмента и первому внедрению.

## Как работать с практикой

В [главе 25](/book-summaries/engineering/dataops-way-to-data-quality/25-building-data-quality-into-dbt-a-complete-guide/) проверки dbt прогоняются на заказах с намеренно нарушенной целостностью. В [главе 42](/book-summaries/engineering/dataops-way-to-data-quality/42-i-wrote-data-quality-tests-for-3-million-nyc-taxi-rides-in-five-minutes/) семь правил проверены на январском файле NYC TLC с 2 964 624 строками. В [главе 54](/book-summaries/engineering/dataops-way-to-data-quality/54-the-seven-deadly-sins-of-ai-generated-data-pipelines/) дважды выполняется одна загрузка и сравнивается итоговое число записей. В [главе 56](/book-summaries/engineering/dataops-way-to-data-quality/56-the-data-quality-and-observability-tools-landscape/) указано, что удалось выполнить локально и какие интеграции требуют готовых внешних сервисов.

## Разбор по главам

Оригинал открывает [введение](/book-summaries/engineering/dataops-way-to-data-quality/00-introduction/). В главе 9 находятся три приложения о методике подсчёта, сопоставлении результатов и источниках обсуждений. В главе 63 есть приложение для коллег из разработки ПО.

### Почему качество данных важно

| Глава | На какой вопрос отвечает | Оригинал |
|---|---|---|
| [1. Четыре процесса команды данных, которые опираются на проверку качества](/book-summaries/engineering/dataops-way-to-data-quality/01-data-quality-testing-is-at-the-core-of-four-critical-data-team-processes/) | Как текущая поставка, выпуск кода и ещё два процесса команды опираются на проверки. | [PDF 7–24](https://datakitchen.io/blog/data-quality-testing-is-at-the-core-of-four-critical-data-team-processes/) |
| [2. Чёрный ящик, полный ошибок в данных](/book-summaries/engineering/dataops-way-to-data-quality/02-the-mystery-box-full-of-data-errors/) | Почему ошибку внутри цепочки трудно локализовать, когда видны только вход и конечный отчёт. | [PDF 25–39](https://datakitchen.io/white-papers/data-quality-the-dataops-way/) |
| [3. Качество и наблюдаемость данных. Когда таблица похожа на питомца, а когда таблицы похожи на стадо](/book-summaries/engineering/dataops-way-to-data-quality/03-data-quality-vs-data-observability-the-pets-and-cattle-of-your-data-estate/) | Где нужен индивидуальный контроль таблицы и где масштабируется единый стандарт. | [PDF 40–48](https://datakitchen.io/blog/data-quality-vs-data-observability-the-pets-and-cattle-of-your-data-estate/) |
| [4. Как перестать платить «налог на качество данных»](/book-summaries/engineering/dataops-way-to-data-quality/04-stop-paying-the-data-quality-tax/) | Как учесть время на повторяющиеся исправления и обсуждения сомнительных цифр. | [PDF 49–55](https://datakitchen.io/blog/stop-paying-the-data-quality-tax/) |
| [5. Как я нарушил SLA, а клиент остался доволен](/book-summaries/engineering/dataops-way-to-data-quality/05-how-i-broke-our-sla-and-delighted-our-customer/) | Почему формальное нарушение SLA и впечатление клиента могут расходиться. | [PDF 56–57](https://datakitchen.io/blog/how-i-broke-our-sla-and-delighted-our-customer/) |
| [6. Экономика качества данных. Когда нужны тесты и сколько на них тратить](/book-summaries/engineering/dataops-way-to-data-quality/06-the-economics-of-data-quality-when-to-test-how-much-to-spend/) | Как выбрать глубину тестирования по цене ошибки и стоимости контроля. | PDF 58–63 |
| [7. Как задержка на одном этапе вызывает сбои на следующих](/book-summaries/engineering/dataops-way-to-data-quality/07-when-timing-goes-wrong-how-latency-issues-cascade/) | Почему опоздание одного источника передаётся следующим шагам. | [PDF 64–67](https://datakitchen.io/blog/when-timing-goes-wrong-how-latency-issues-cascade/) |
| [8. Почему инженеры данных не пишут тесты и как нас за этот вопрос раскритиковали на Reddit](/book-summaries/engineering/dataops-way-to-data-quality/08-we-got-roasted-on-reddit-for-asking-why-data-engineers-dont-test/) | Что инженеры назвали препятствиями для тестирования в первом обсуждении Reddit. | [PDF 68–77](https://datakitchen.io/blog/we-got-roasted-on-reddit-for-asking-why-data-engineers-dont-test/) |
| [9. «Смотрим на число строк и надеемся на лучшее»](/book-summaries/engineering/dataops-way-to-data-quality/09-we-just-eyeball-row-counts-and-pray/) | Какие причины повторились в 849 комментариях и как авторы их считали. | [PDF 78–95](https://datakitchen.io/blog/we-just-eyeball-row-counts-and-pray/) |
| [10. Во что компании обходятся данные, которыми трудно пользоваться](/book-summaries/engineering/dataops-way-to-data-quality/10-a-data-usability-crisis-is-costing-your-company/) | Как сложность использования исправных данных отнимает время у потребителей. | [PDF 96–104](https://datakitchen.io/blog/a-data-usability-crisis-is-costing-your-company/) |

### Культура и организация работы

| Глава | На какой вопрос отвечает | Оригинал |
|---|---|---|
| [11. Семь смертных грехов в работе над качеством данных](/book-summaries/engineering/dataops-way-to-data-quality/11-the-seven-deadly-sins-of-data-quality/) | Какие привычки команды приводят к повторению одних и тех же дефектов. | [PDF 106–114](https://datakitchen.io/blog/the-seven-deadly-sins-of-data-quality/) |
| [12. Как ошибки в данных превращаются в повод стыдить коллег](/book-summaries/engineering/dataops-way-to-data-quality/12-the-data-errors-shame-game/) | Как публичный поиск виноватого мешает сообщать о сбоях. | [PDF 115–121](https://datakitchen.io/blog/the-data-errors-shame-game-why-data-engineers-avoid-harsh-truths/) |
| [13. Признаёт ли команда проблемы с качеством данных](/book-summaries/engineering/dataops-way-to-data-quality/13-is-your-team-in-denial-about-data-quality/) | Как увидеть проблему с качеством, которую отдел привык считать нормой. | [PDF 122–128](https://datakitchen.io/blog/is-your-team-in-denial-of-data-quality/) |
| [14. Эффект страуса. Почему после выпуска команда перестаёт следить за данными](/book-summaries/engineering/dataops-way-to-data-quality/14-the-ostrich-problem-when-your-data-team-stops-caring-after-deployment/) | Почему проверка при выпуске не заменяет наблюдения за дальнейшей работой. | [PDF 129–135](https://datakitchen.io/blog/the-ostrich-problem-your-data-team-thinks-their-job-ends-at-deployment/) |
| [15. Перемены в работе над качеством данных начинаются с вас](/book-summaries/engineering/dataops-way-to-data-quality/15-the-data-quality-revolution-starts-with-you/) | С какой перемены в собственной работе можно начать улучшение. | [PDF 136–141](https://datakitchen.io/blog/the-data-quality-revolution-starts-with-you/) |
| [16. Пять организационных ошибок команд данных](/book-summaries/engineering/dataops-way-to-data-quality/16-the-five-organizational-sins-of-data-teams/) | Какие организационные разрывы делают технические улучшения недолговечными. | [PDF 142–148](https://datakitchen.io/blog/the-five-organizational-sins-of-data-teams/) |
| [17. Что мы упускаем, когда говорим о продуктах данных](/book-summaries/engineering/dataops-way-to-data-quality/17-youre-thinking-about-data-products-all-wrong/) | Как рассматривать работу над продуктом данных на протяжении его жизни. | [PDF 149–156](https://datakitchen.io/blog/youre-thinking-about-data-products-all-wrong/) |
| [18. Кто сопровождает общую бизнес-логику и почему этой работой пренебрегают](/book-summaries/engineering/dataops-way-to-data-quality/18-process-guardianship-the-most-valuable-work-you-are-probably-not-doing/) | Кто отвечает за общие определения метрик и историю их изменений. | [PDF 157–165](https://datakitchen.io/blog/process-guardianship-the-most-valuable-data-engineering-work-youre-probably-not-doing/) |
| [19. Как руководителям по качеству данных влиять на решения и избежать трагедии общих ресурсов](/book-summaries/engineering/dataops-way-to-data-quality/19-how-data-quality-leaders-can-gain-influence-and-avoid-the-tragedy-of-the-commons/) | Как договориться об ответственности за общий ресурс при разных интересах подразделений. | [PDF 166–173](https://datakitchen.io/blog/how-data-quality-leaders-can-gain-influence-and-avoid-the-tragedy-of-the-commons/) |
| [20. Как повысить эффективность команды данных](/book-summaries/engineering/dataops-way-to-data-quality/20-how-do-i-get-my-data-team-more-efficient/) | Почему занятость каждого специалиста не равна результативности всей команды. | [PDF 174–181](https://datakitchen.io/blog/how-do-i-get-my-data-team-more-efficient/) |

### Стратегия тестирования

| Глава | На какой вопрос отвечает | Оригинал |
|---|---|---|
| [21. Shift-left и shift-down. Где размещать проверки качества](/book-summaries/engineering/dataops-way-to-data-quality/21-shift-left-shift-down-how-to-take-control-of-data-quality/) | Чем ранняя проверка данных отличается от проверки изменения в разработке. | [PDF 183–189](https://datakitchen.io/blog/flip-the-script-on-data-quality-shift-left-shift-down-and-take-control/) |
| [22. Как повысить надёжность данных с помощью покрытия тестами](/book-summaries/engineering/dataops-way-to-data-quality/22-scaling-data-reliability-the-definitive-guide-to-test-coverage/) | Как считать охват проверками и находить непроверенные участки. | [PDF 190–199](https://datakitchen.io/blog/scaling-data-reliability-the-definitive-guide-to-test-coverage/) |
| [23. Покрытие тестами качества данных в медальонной архитектуре](/book-summaries/engineering/dataops-way-to-data-quality/23-data-quality-test-coverage-in-a-medallion-data-architecture/) | Какие дефекты ловить при переходах между слоями bronze, silver и gold. | [PDF 200–209](https://datakitchen.io/blog/data-quality-test-coverage-in-a-medallion-data-architecture/) |
| [24. Гонка за качеством данных в медальонной архитектуре](/book-summaries/engineering/dataops-way-to-data-quality/24-the-race-for-data-quality-in-a-medallion-architecture/) | Как выбрать очередность вложений в проверки по слоям. | [PDF 210–220](https://datakitchen.io/blog/the-race-for-data-quality-in-a-medallion-architecture/) |
| [25. Как встроить проверки качества данных в dbt](/book-summaries/engineering/dataops-way-to-data-quality/25-building-data-quality-into-dbt-a-complete-guide/) | Как связать тесты dbt с приёмкой источника и проверкой результата модели. | PDF 221–234 |
| [26. Как контракт данных распределяет ответственность за качество у источника](/book-summaries/engineering/dataops-way-to-data-quality/26-data-contracts-shifting-the-burden-of-quality-to-the-source/) | Что поставщик и потребитель могут действительно зафиксировать в контракте. | PDF 235–248 |
| [27. Первый год практики контроля качества данных. От первых проверок до расширения охвата](/book-summaries/engineering/dataops-way-to-data-quality/27-building-and-scaling-a-data-quality-practice-the-first-year/) | Как постепенно расширять практику контроля в течение первого года. | PDF 249–255 |
| [28. Какие последствия ошибок упускают привычные показатели качества](/book-summaries/engineering/dataops-way-to-data-quality/28-impact-dimensions-cure-a-data-quality-blind-spot/) | Как группировать дефекты по их последствиям для потребителя. | [PDF 256–265](https://datakitchen.io/blog/impact-dimensions/) |
| [29. Как узнать правила качества данных, которые коллеги держат в голове](/book-summaries/engineering/dataops-way-to-data-quality/29-your-best-data-quality-rules-live-in-someone-elses-head/) | Как получить правило качества из опыта человека, который работает с данными. | [PDF 266–274](https://datakitchen.io/blog/best-data-quality-rules-live-in-someone-elses-head/) |
| [30. Чертёж и пожарная сигнализация. Что покрытие тестами показывает сверх lineage](/book-summaries/engineering/dataops-way-to-data-quality/30-the-blueprint-or-the-fire-alarm-panel-why-data-test-coverage-beats-data-lineage/) | Почему две версии запроса с одинаковыми связями могут дать разные суммы. | [PDF 275–288](https://datakitchen.io/blog/test-coverage-beats-data-lineage/) |
| [31. Контракт данных как квитанция о приёмке](/book-summaries/engineering/dataops-way-to-data-quality/31-the-data-contract-is-your-receipt/) | Каким свидетельством подтвердить приёмку конкретной поставки. | [PDF 289–298](https://datakitchen.io/blog/the-data-contract-is-your-receipt/) |
| [32. Четыре точки медальонной архитектуры, в которых особенно важны проверки данных](/book-summaries/engineering/dataops-way-to-data-quality/32-the-four-points-in-your-medallion-architecture-where-data-testing-really-matters/) | На каких четырёх границах архитектуры особенно важно проверить партию. | [PDF 299–316](https://datakitchen.io/blog/medallion-architecture-four-points-data-testing/) |
| [33. Как проверять каждый слой медальонной архитектуры на OneLake](/book-summaries/engineering/dataops-way-to-data-quality/33-testing-every-layer-of-the-medallion-architecture-now-with-onelake-at-the-center/) | Как разместить проверки на слоях OneLake. | [PDF 317–326](https://datakitchen.io/blog/testgen-onelake-medallion-architecture-testing/) |

### Мониторинг и наблюдаемость

| Глава | На какой вопрос отвечает | Оригинал |
|---|---|---|
| [34. Наблюдаемость данных. За чем следить и зачем](/book-summaries/engineering/dataops-way-to-data-quality/34-data-observability-what-to-monitor-and-why-it-matters/) | Чем наблюдение за запуском дополняет проверку результата. | [PDF 328–335](https://datakitchen.io/blog/the-five-use-cases-in-data-observability-overview/) |
| [35. Шесть типов дашбордов качества данных](/book-summaries/engineering/dataops-way-to-data-quality/35-the-six-types-of-data-quality-dashboards/) | Как различать шесть типов дашбордов по решениям их пользователей. | [PDF 336–350](https://datakitchen.io/blog/the-six-types-of-data-quality-dashboards/) |
| [36. Как настроить оповещения о качестве данных и избежать усталости от них](/book-summaries/engineering/dataops-way-to-data-quality/36-data-quality-alerting-avoiding-alert-fatigue/) | Как назначить адресата сигнала и уменьшить поток бесполезных уведомлений. | PDF 351–356 |
| [37. Почему дашборд качества данных не помогает команде и как его исправить](/book-summaries/engineering/dataops-way-to-data-quality/37-why-your-data-quality-dashboard-isnt-working-and-what-to-do-about-it/) | Почему даже технически исправный дашборд может не помочь дежурному. | [PDF 357–366](https://datakitchen.io/blog/why-your-data-quality-dashboard-isnt-working-and-what-to-do-about-it/) |
| [38. Блокирующие проверки в Databricks. Как остановить ошибочные данные до передачи потребителю](/book-summaries/engineering/dataops-way-to-data-quality/38-data-production-tripwires-in-databricks-stop-bad-data-before-it-reaches-production/) | Как сделать проверку условием передачи данных в Databricks. | [PDF 367–376](https://datakitchen.io/blog/data-production-tripwires-in-databricks-stop-bad-data-before-it-reaches-production/) |

### Внедрение и разбор кейсов

| Глава | На какой вопрос отвечает | Оригинал |
|---|---|---|
| [39. Антипаттерны тестирования данных. Почему тесты подводят команду](/book-summaries/engineering/dataops-way-to-data-quality/39-data-testing-anti-patterns-why-your-tests-are-failing-you/) | Какие тесты дают ложное ощущение защиты и как проверить их границы. | PDF 378–385 |
| [40. Три примера серьёзных сбоев в данных и меры, которые их предотвратили](/book-summaries/engineering/dataops-way-to-data-quality/40-three-data-quality-disasters-and-how-they-were-averted/) | Какие меры остановили три разных сбоя до серьёзных последствий. | PDF 386–392 |
| [41. Когда можно обойтись без тестов и как ограничить затраты на проверки](/book-summaries/engineering/dataops-way-to-data-quality/41-when-not-to-test-setting-reasonable-bounds-on-data-quality-effort/) | Когда дополнительная проверка стоит дороже предотвращаемой ошибки. | PDF 393–397 |
| [42. Как я за пять минут написал тесты для данных о трёх миллионах поездок нью-йоркского такси](/book-summaries/engineering/dataops-way-to-data-quality/42-i-wrote-data-quality-tests-for-3-million-nyc-taxi-rides-in-five-minutes/) | Почему все 62 сгенерированных теста прошли на выборке с невозможными тарифами. | [PDF 398–407](https://datakitchen.io/blog/data-quality-tests-3-million-nyc-taxi-rides-five-minutes/) |
| [43. Ошибки в данных в розыске. Дела 2026 года](/book-summaries/engineering/dataops-way-to-data-quality/43-data-qualitys-most-wanted-the-2026-case-files/) | Чему четыре публичных случая учат о сверке, правах и миграции данных. | [PDF 408–414](https://datakitchen.io/blog/data-qualitys-most-wanted-the-2026-case-files/) |
| [44. Почему сложно проверять коммерческие данные фармацевтических компаний](/book-summaries/engineering/dataops-way-to-data-quality/44-why-testing-commercial-pharma-data-is-harder-than-anyone-tells-you/) | Почему расхождения между отраслевыми источниками переживают технически успешную загрузку. | [PDF 415–421](https://datakitchen.io/blog/why-testing-commercial-pharma-data-is-harder-than-anyone-tells-you/) |
| [45. IQVIA, специализированные аптеки и собственные файлы. Где вероятнее всего встретить ошибки](/book-summaries/engineering/dataops-way-to-data-quality/45-iqvia-specialty-pharmacy-and-your-own-files-the-commercial-data-most-likely-to-be-wrong/) | Как различить ошибку загрузки и ретроспективный пересчёт показателя поставщиком. | [PDF 422–428](https://datakitchen.io/blog/commercial-pharma-data-most-likely-to-be-wrong/) |
| [46. Иллюзия чистых данных. Какие идентификаторы в фармацевтике упускают универсальные инструменты](/book-summaries/engineering/dataops-way-to-data-quality/46-the-illusion-of-clean-data-the-pharma-identifiers-generic-tools-never-check/) | Что именно доказывают форма, контрольная цифра и вхождение в справочник. | [PDF 429–437](https://datakitchen.io/blog/npi-ndc-icd-validation-tests/) |

### ИИ и качество данных

| Глава | На какой вопрос отвечает | Оригинал |
|---|---|---|
| [47. Что может пойти не так, если передать эти данные языковой модели](/book-summaries/engineering/dataops-way-to-data-quality/47-sure-go-ahead-and-feed-that-data-to-the-llm-what-could-possibly-go-wrong/) | Как проверять и входы для модели, и написанный ею SQL. | [PDF 439–450](https://datakitchen.io/blog/sure-go-ahead-and-feed-that-data-to-the-llm-what-could-possibly-go-wrong/) |
| [48. Формула успеха ИИ по версии авторов. DT + DX + CTX = 10×](/book-summaries/engineering/dataops-way-to-data-quality/48-the-equation-for-ai-success-dt-dx-ctx-10x/) | Для чего модели нужны проверенные данные, понятный слой и деловые определения. | [PDF 451–465](https://datakitchen.io/blog/the-equation-for-ai-success-dt-dx-ctx-10x/) |
| [49. DataOps, FITT и тестирование данных. Как авторы обосновывают десятикратный рост производительности с ИИ](/book-summaries/engineering/dataops-way-to-data-quality/49-dataops-fitt-data-testing-10x-data-engineering-productivity-with-ai/) | Как сравнить несколько реализаций на независимых тестовых данных. | [PDF 466–485](https://datakitchen.io/blog/dataops-fitt-data-testing-10x-data-engineering-productivity-with-ai/) |
| [50. Контекст как инфраструктура. Шесть категорий для анализа данных с ИИ](/book-summaries/engineering/dataops-way-to-data-quality/50-context-as-infrastructure-the-six-category-framework-for-ai-ready-data-analysis/) | Как поддерживать шесть видов контекста с разными сроками актуальности. | [PDF 486–505](https://datakitchen.io/blog/context-as-infrastructure-the-six-category-framework-for-ai-ready-data-analysis/) |
| [51. Как сократить расход токенов, если ИИ может запрашивать результаты проверок и наблюдений](/book-summaries/engineering/dataops-way-to-data-quality/51-stop-burning-tokens-data-observability-and-quality-as-your-ais-system-of-record/) | Какие вопросы стоит один раз превратить в регулярно исполняемое правило. | [PDF 506–508](https://datakitchen.io/blog/stop-burning-tokens-data-quality-observability-ai-system-of-record/) |
| [52. Как использовать ИИ при принятии решений о качестве и наблюдаемости данных](/book-summaries/engineering/dataops-way-to-data-quality/52-put-your-ai-at-the-center-of-your-data-quality-and-observability-decision-making-process/) | Как соединить тест, код, прошлую заявку и расписание потребителя при расследовании. | [PDF 509–516](https://datakitchen.io/blog/put-your-ai-at-the-center-of-your-data-quality-decisions/) |
| [53. Как устроен агент, который исправляет ошибки в данных под контролем человека](/book-summaries/engineering/dataops-way-to-data-quality/53-agents-to-fix-data-quality-automatically-with-control-a-design-pattern/) | Как связать предложения агента, разрешение человека и журнал исполнения. | [PDF 517–523](https://datakitchen.io/blog/agents-fix-data-quality-automatically-with-control/) |
| [54. Семь смертных грехов в обработке данных с помощью кода, написанного ИИ](/book-summaries/engineering/dataops-way-to-data-quality/54-the-seven-deadly-sins-of-ai-generated-data-pipelines/) | Почему повторная загрузка и неизменный lineage могут скрыть ошибочный итог. | [PDF 524–534](https://datakitchen.io/blog/seven-deadly-sins-of-ai-generated-data-pipelines/) |

### Справочные материалы и инструменты

| Глава | На какой вопрос отвечает | Оригинал |
|---|---|---|
| [55. Как выбрать инструменты для проверки качества данных](/book-summaries/engineering/dataops-way-to-data-quality/55-a-practical-guide-to-selecting-data-quality-tools/) | Как выбрать средство проверки по месту дефекта и требуемой реакции. | PDF 536–542 |
| [56. Обзор инструментов для качества и наблюдаемости данных](/book-summaries/engineering/dataops-way-to-data-quality/56-the-data-quality-and-observability-tools-landscape/) | Какие задачи закрывают инструменты для проверок, мониторинга и зависимостей. | [PDF 543–551](https://datakitchen.io/blog/the-2026-open-source-data-quality-and-data-observability-landscape/) |
| [57. Коммерческие инструменты для качества и наблюдаемости данных в 2026 году](/book-summaries/engineering/dataops-way-to-data-quality/57-the-2026-data-quality-and-data-observability-commercial-software-landscape/) | Как авторы сравнивают коммерческие предложения и модели оплаты. | [PDF 552–556](https://datakitchen.io/blog/the-2026-data-quality-and-data-observability-commercial-software-landscape/) |
| [58. Открытые инструменты для профилирования данных в 2026 году](/book-summaries/engineering/dataops-way-to-data-quality/58-the-2026-open-source-data-profiling-software-landscape/) | Какие открытые средства помогают изучить неизвестный набор данных. | [PDF 557–562](https://datakitchen.io/blog/the-2026-open-source-data-profiling-software-landscape/) |
| [59. Как консультанту привлекать клиентов с помощью открытого инструмента DataKitchen TestGen](/book-summaries/engineering/dataops-way-to-data-quality/59-the-consultants-growth-playbook-accelerating-client-acquisition-with-datakitchen-open-source-testgen/) | Как авторы предлагают консультанту показать клиенту результат профилирования. | [PDF 563–574](https://datakitchen.io/blog/the-consultants-growth-playbook-accelerating-client-acquisition-and-retention-with-datakitchen-open-source-testgen/) |
| [60. Миллиард долларов венчурных инвестиций в наблюдаемость данных. Почему авторы ожидают проблем](/book-summaries/engineering/dataops-way-to-data-quality/60-1-billion-in-data-observability-vc-investment-this-is-not-going-to-end-well/) | На чём основана авторская оценка инвестиций в рынок наблюдаемости и его перспектив. | [PDF 575–587](https://datakitchen.io/blog/1-billion-ivc-investment-this-is-not-going-to-end-well/) |
| [61. Почему поставщиков инструментов качества и наблюдаемости данных так много](/book-summaries/engineering/dataops-way-to-data-quality/61-there-are-a-lot-of-freaking-data-quality-and-data-observability-vendors/) | Почему решения разных поставщиков закрывают разные части одной задачи. | [PDF 588–592](https://datakitchen.io/blog/there-are-a-lot-of-freaking-data-quality-and-data-observability-vendors/) |
| [62. Как авторы насчитали у Microsoft девятнадцать инструментов качества данных в 2026 году](/book-summaries/engineering/dataops-way-to-data-quality/62-there-is-no-microsoft-data-quality-tool-in-2026-there-are-nineteen/) | Что именно включили авторы в свой перечень девятнадцати средств Microsoft. | [PDF 593–613](https://datakitchen.io/blog/no-microsoft-data-quality-tool-there-are-nineteen/) |
| [63. С чего начать внедрение DataOps в 2026 году](/book-summaries/engineering/dataops-way-to-data-quality/63-where-to-actually-start-with-dataops-in-2026/) | Как выбрать первый рабочий процесс для внедрения DataOps. | [PDF 614–619](https://datakitchen.io/blog/where-to-actually-start-with-dataops-in-2026/) |

[Дополнительные материалы и 42 ссылки из книги](/book-summaries/engineering/dataops-way-to-data-quality/64-read-more/).
