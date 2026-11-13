---
title: "Escaping the Build Trap — конспект книги"
head:
  - tag: title
    content: "Escaping the Build Trap: конспект книги | Инжиниринг Данных"
description: "Конспект книги Escaping the Build Trap на русском. Build trap, роль продакт-менеджера, стратегия, Product Kata, метрики. Разбор 25 глав для инженера данных."
author: "Melissa Perri"
sidebar:
  order: 0
  label: "Обзор книги"
tags:
  - books
  - product-management
---

**Escaping the Build Trap: How Effective Product Management Creates Real Value** — книга Melissa Perri (O'Reilly, 2018). Она о том, почему компании строят много фич, но не растут, и как выйти из этой ловушки. В книге 25 глав в пяти частях, послесловие и приложение. Сквозной пример — вымышленная компания Marquetly, школа онлайн-курсов. За книгу она проходит путь от «делаем фичи» к «решаем проблемы клиентов».

> Это подробный пересказ на русском, а не перевод. За полным текстом идите в оригинал.

![Карта книги: пять частей от build trap до product-led компании](/assets/escaping-the-build-trap/ch00-book-map.png)

## О чём книга простыми словами

Многие компании измеряют успех тем, сколько фич они выпустили. Это и есть build trap (ловушка «просто строим»). Команды заняты, релизы идут, а клиентам и бизнесу лучше не становится. Автор называет это мышлением `output`.

Выход — думать о `outcome`: что изменилось для клиента и для бизнеса. Книга показывает, как это сделать. Нужны сильные продакт-менеджеры, стратегия на четырёх уровнях, процесс поиска решений через проблему (`Product Kata`) и организация, которая это поддерживает: встречи, награды, бюджет и безопасность для ошибок.

Главная модель книги — обмен ценностью. Компания даёт клиенту ценность, клиент даёт ценность компании. Продукт-менеджмент отвечает за то, чтобы этот обмен работал.

## Что нужно знать заранее

- Что такое продукт, фича и релиз. Других знаний не нужно.
- Желательно знать, что такое метрика и дашборд. Тогда главы о метриках (16) и коммуникации (20) будут понятнее.
- Для практических блоков полезны `dbt`, SQL и общее понимание хранилища данных. Книга сама о продакт-менеджменте, а не о данных.
- Если интересует, какие метрики выбирать, посмотрите [конспект Lean Analytics](/book-summaries/business/lean-analytics/).

## Зачем читать

Сегодня от дата-инженера ждут продуктового мышления: говорить с бизнесом на его языке и понимать, как строится продукт. Эта книга даёт такую картину.

- **Output и outcome.** Вы отличите «сколько сделали» от «что изменилось». Это основа хороших метрик и дашбордов.
- **Откуда берутся требования.** Метрики и отчёты идут из стратегии: vision → strategic intents → product initiatives → options. Вы поймёте, зачем бизнес просит именно эту цифру.
- **Язык продакт-менеджера.** `Product Kata`, `leading` и `lagging` метрики, эксперименты, roadmap по стадиям. Вам будет проще на встречах с продуктом.
- **Свои приоритеты.** Вы сможете спросить: «Какую проблему решает эта таблица?» и отказаться от работы ради работы.
- **Выбор компании.** Шесть вопросов из приложения помогают понять на собеседовании, работает ли компания на результат.

Книга хорошо дополняет [конспект Lean Analytics](/book-summaries/business/lean-analytics/). Lean Analytics отвечает, **что** измерять. Escaping the Build Trap — **как** компания выбирает цели и работает с ними.

## Как устроена книга

| Часть | Главы | О чём |
|---|---|---|
| I. The Build Trap | 1–5 | Что такое ловушка, обмен ценностью, проект и продукт, типы компаний |
| II. The Role of the Product Manager | 6–9 | Плохие и хорошие продакт-менеджеры, карьера, организация команд |
| III. Strategy | 10–14 | Что такое стратегия, разрывы Bungay, четыре уровня стратегии, портфель |
| IV. Product Management Process | 15–19 | Product Kata, метрики успеха, исследование проблемы и решений, разработка |
| V. The Product-Led Organization | 20–25 | Коммуникация, стимулы, безопасность, бюджет, клиент, итог Marquetly |
| Послесловие и приложение | — | Уроки автора и шесть вопросов о компании |

## Главные идеи

| Идея | Где |
|---|---|
| Build trap: успех измеряют выпуском фич, а не результатом | [Глава 1](/book-summaries/business/escaping-the-build-trap/01-value-exchange-system/) |
| Продукт живёт и растёт, проект заканчивается на релизе | [Глава 3](/book-summaries/business/escaping-the-build-trap/03-projects-products-services/) |
| Продакт-менеджер владеет «почему», команда — «что» | [Глава 7](/book-summaries/business/escaping-the-build-trap/07-great-product-manager/) |
| Команды вокруг value stream и целей, а не компонентов | [Глава 9](/book-summaries/business/escaping-the-build-trap/09-organizing-teams/) |
| Стратегия — рамка для решений, а не план | [Глава 10](/book-summaries/business/escaping-the-build-trap/10-what-is-strategy/) |
| Четыре уровня: vision, intents, initiatives, options | [Глава 12](/book-summaries/business/escaping-the-build-trap/12-strategic-framework/) |
| Product Kata: шесть вопросов на каждый цикл | [Глава 15](/book-summaries/business/escaping-the-build-trap/15-product-kata/) |
| Leading и lagging метрики, AARRR и HEART | [Глава 16](/book-summaries/business/escaping-the-build-trap/16-direction-and-success-metrics/) |
| Строим, чтобы учиться: concierge, Wizard of Oz, concept test | [Глава 18](/book-summaries/business/escaping-the-build-trap/18-solution-exploration/) |
| Работа готова, когда достигнута цель | [Глава 19](/book-summaries/business/escaping-the-build-trap/19-building-and-optimizing/) |
| Бюджет по стадиям, как у инвестора | [Глава 23](/book-summaries/business/escaping-the-build-trap/23-budgeting/) |

## Как читать

- **Новичок.** Читайте по порядку. На первом проходе берите «Главную мысль», схемы и «Ключевые термины».
- **Analytics engineer, аналитик.** Главы 15–19: Product Kata, метрики, эксперименты. Потом глава 12: откуда берутся цели.
- **Data engineer.** Главы 1–3 (output и outcome, продукт и проект), 9 (команды), 16 (метрики), 20 (product operations и отчёты для руководства).
- **Руководитель.** Части III и V: стратегия, коммуникация, стимулы, бюджет. Потом шесть вопросов в главе 26.

## Разбор по главам

### Часть I. The Build Trap

| Глава | Тема |
|---|---|
| [1. Обмен ценностью](/book-summaries/business/escaping-the-build-trap/01-value-exchange-system/) | Что такое build trap, история Marquetly, value exchange |
| [2. Ограничения обмена ценностью](/book-summaries/business/escaping-the-build-trap/02-constraints-on-value-exchange/) | Что мешает ценности у клиента и в компании |
| [3. Проекты, продукты и сервисы](/book-summaries/business/escaping-the-build-trap/03-projects-products-services/) | Чем они отличаются и почему проекты ведут в ловушку |
| [4. Product-led организация](/book-summaries/business/escaping-the-build-trap/04-product-led-organization/) | Sales-led, visionary-led, technology-led и product-led |
| [5. Что мы знаем и чего нет](/book-summaries/business/escaping-the-build-trap/05-what-we-know/) | Known и unknown, роль PM в неопределённости |

### Часть II. The Role of the Product Manager

| Глава | Тема |
|---|---|
| [6. Плохие архетипы PM](/book-summaries/business/escaping-the-build-trap/06-bad-pm-archetypes/) | Mini-CEO, официант, бывший проджект-менеджер |
| [7. Хороший продакт-менеджер](/book-summaries/business/escaping-the-build-trap/07-great-product-manager/) | Бизнес, технологии и UX, владение «почему» |
| [8. Карьера продакт-менеджера](/book-summaries/business/escaping-the-build-trap/08-pm-career-path/) | Уровни от APM до CPO, тактика и стратегия |
| [9. Как организовать команды](/book-summaries/business/escaping-the-build-trap/09-organizing-teams/) | Компоненты, фичи, value stream |

### Часть III. Strategy

| Глава | Тема |
|---|---|
| [10. Что такое стратегия](/book-summaries/business/escaping-the-build-trap/10-what-is-strategy/) | Пример Netflix, стратегия против плана |
| [11. Стратегические разрывы](/book-summaries/business/escaping-the-build-trap/11-strategic-gaps/) | Knowledge, alignment и effects gap |
| [12. Стратегическая рамка](/book-summaries/business/escaping-the-build-trap/12-strategic-framework/) | Strategy deployment, четыре уровня стратегии |
| [13. Видение и strategic intents](/book-summaries/business/escaping-the-build-trap/13-vision-and-strategic-intents/) | Видение компании и главные цели |
| [14. Видение продукта и портфель](/book-summaries/business/escaping-the-build-trap/14-product-vision-and-portfolio/) | Initiatives, options, портфель, роль CPO |

### Часть IV. Product Management Process

| Глава | Тема |
|---|---|
| [15. Product Kata](/book-summaries/business/escaping-the-build-trap/15-product-kata/) | Шесть вопросов, цель команды |
| [16. Направление и метрики успеха](/book-summaries/business/escaping-the-build-trap/16-direction-and-success-metrics/) | AARRR, HEART, leading и lagging |
| [17. Исследование проблемы](/book-summaries/business/escaping-the-build-trap/17-problem-exploration/) | Интервью, корень проблемы |
| [18. Исследование решений](/book-summaries/business/escaping-the-build-trap/18-solution-exploration/) | Эксперименты, MVP |
| [19. Разработка и оптимизация](/book-summaries/business/escaping-the-build-trap/19-building-and-optimizing/) | Story mapping, Cost of Delay, Definition of Done |

### Часть V. The Product-Led Organization

| Глава | Тема |
|---|---|
| [20. Коммуникация через результат](/book-summaries/business/escaping-the-build-trap/20-outcome-focused-communication/) | Kodak, встречи, roadmap, product operations |
| [21. Награды и стимулы](/book-summaries/business/escaping-the-build-trap/21-rewards-and-incentives/) | Бонусы за output, стимулы продаж |
| [22. Безопасность и обучение](/book-summaries/business/escaping-the-build-trap/22-safety-and-learning/) | Право на ошибку, границы экспериментов |
| [23. Бюджет](/book-summaries/business/escaping-the-build-trap/23-budgeting/) | Годовой бюджет и деньги по стадиям |
| [24. Клиентоориентированность](/book-summaries/business/escaping-the-build-trap/24-customer-centricity/) | Amazon, John Deere |
| [25. Marquetly: product-led компания](/book-summaries/business/escaping-the-build-trap/25-marquetly-product-led/) | Итог истории Marquetly |
| [26. Послесловие и шесть вопросов](/book-summaries/business/escaping-the-build-trap/26-afterword-and-six-questions/) | Уроки автора, вопросы о компании |

Каждая страница содержит главную мысль, раздел «О чём глава», итоги, ключевые термины, выводы для дата-инженера и вопросы для самопроверки.
