---
title: Lean Analytics — конспект книги
head:
  - tag: title
    content: "Lean Analytics: конспект книги на русском | Инжиниринг Данных"
description: "Конспект книги Lean Analytics на русском. Зачем читать, как измерять стартап, метрики по бизнес-моделям и стадиям, разбор по главам."
sidebar:
  order: 0
  label: "Обзор книги"
tags:
  - books
  - metrics
  - product-analytics
---

**Lean Analytics** — книга Алистера Кролла и Бена Йосковица. Она учит измерять стартап и принимать решения по данным. Это конспект на русском с разбором по главам и схемами.

> Это собственный пересказ, а не дословный перевод. За полным текстом и примерами идите в оригинал. Схемы нарисованы заново по содержанию глав.

## Зачем нужна эта книга

Дата-инженер строит пайплайны и витрины. Но данные нужны не сами по себе. Они нужны, чтобы бизнес принимал решения. Эта книга учит понимать, **какие данные нужны бизнесу и почему**.

- **Язык бизнеса.** Вы поймёте, что такое `churn`, `LTV`, `CAC`, `retention` и откуда они берутся.
- **Правильные метрики.** Вы отличите полезную метрику от «метрики для красоты» (vanity metric).
- **Домены.** Книга разбирает шесть бизнес-моделей: e-commerce, SaaS, мобильное приложение, медиа, пользовательский контент, маркетплейс. Для каждой есть свои ключевые метрики.
- **Стадии продукта.** Метрики зависят от стадии: от поиска проблемы до масштаба.
- **Ориентиры.** Книга даёт примерные «нормальные» значения метрик, чтобы понимать, хорошо вам или плохо.
- **Лучшие требования к данным.** Когда вы понимаете, зачем метрика, вы делаете модель данных точнее. Вы задаёте аналитику и продукту правильные вопросы.

## Для кого

| Роль | Что получит |
|---|---|
| Дата-инженер | Понимание, какие события и таблицы нужны для метрик продукта |
| Аналитик, BI-разработчик | Рамки для выбора метрик и объяснения их бизнесу |
| Продакт, маркетолог | Метод проверки гипотез без догадок |
| Основатель, инвестор | Способ оценить стартап по цифрам |
| Интрапренёр в большой компании | Применение Lean внутри корпорации |

Книга писалась про веб-стартапы. Но подходы работают и в локальном бизнесе, B2B, политических кампаниях и внутри крупных компаний.

## Как устроена книга

Книга основана на интервью со ста с лишним основателями и инвесторами и на 30+ кейсах. В конце каждой главы есть вопросы для самопроверки.

| Часть | О чём | Главы книги |
|---|---|---|
| I. Основы | Lean Startup и аналитика, фреймворки | 1–5 |
| II. Lean Analytics на практике | Шесть бизнес-моделей, пять стадий, One Metric That Matters | 6–20 |
| III. Ориентиры | Что такое «нормально» для каждой модели | 21–27 |
| IV. Внедрение | Нет базы для сравнения, enterprise, интрапренёры | 28–31 |

## Разбор по главам

### Часть I. Основы

| Глава | Тема |
|---|---|
| [1. Мы все лжём](/resources/lean-analytics/01-we-are-all-liars/) | Почему интуиции мало, цикл Lean, пример Airbnb |
| [2. Как вести счёт](/resources/lean-analytics/02-how-to-keep-score/) | Хорошие метрики, типы метрик, vanity, цикл Lean Analytics |
| [3. Чем заняться](/resources/lean-analytics/03-deciding-what-to-do/) | Выбор идеи, Lean Canvas |
| [4. Data-driven и data-informed](/resources/lean-analytics/04-data-driven-vs-data-informed/) | Локальный максимум, девять советов по данным |
| [5. Аналитические фреймворки](/resources/lean-analytics/05-analytics-frameworks/) | AARRR, Engines of Growth, пирамида Эллиса |

### Часть II. Lean Analytics на практике

| Глава | Тема |
|---|---|
| [6. One Metric That Matters](/resources/lean-analytics/06-one-metric-that-matters/) | Одна главная метрика |
| [7. В каком вы бизнесе](/resources/lean-analytics/07-what-business-are-you-in/) | Бизнес-модель и рычаги роста |
| [8. E-commerce](/resources/lean-analytics/08-ecommerce/) | Воронка, режимы отношений |
| [9. SaaS](/resources/lean-analytics/09-saas/) | Churn, CAC, LTV |
| [10. Мобильное приложение](/resources/lean-analytics/10-mobile-app/) | DAU, ARPU, монетизация |
| [11. Медиа-сайт](/resources/lean-analytics/11-media-site/) | Аудитория, реклама, CTR |
| [12. Пользовательский контент](/resources/lean-analytics/12-user-generated-content/) | Воронка вовлечения |
| [13. Двусторонние маркетплейсы](/resources/lean-analytics/13-two-sided-marketplaces/) | Курица и яйцо, доверие |
| [14. На какой вы стадии](/resources/lean-analytics/14-what-stage-are-you-at/) | Пять стадий |
| [15. Стадия 1: Empathy](/resources/lean-analytics/15-stage-one-empathy/) | Интервью и проблема |
| [16. Стадия 2: Stickiness](/resources/lean-analytics/16-stage-two-stickiness/) | Удержание, MVP |
| [17. Стадия 3: Virality](/resources/lean-analytics/17-stage-three-virality/) | Вирусный коэффициент |
| [18. Стадия 4: Revenue](/resources/lean-analytics/18-stage-four-revenue/) | LTV и CAC |
| [19. Стадия 5: Scale](/resources/lean-analytics/19-stage-five-scale/) | Каналы, Three-Threes |
| [20. Модель и стадия](/resources/lean-analytics/20-model-and-stage-drive-the-metric/) | Выбор метрики |

### Часть III. Ориентиры

| Глава | Тема |
|---|---|
| [21. Достаточно ли хорошо](/resources/lean-analytics/21-am-i-good-enough/) | Что считать нормой |
| [22. E-commerce: ориентиры](/resources/lean-analytics/22-ecommerce-lines-in-the-sand/) | Конверсия, брошенные корзины |
| [23. SaaS: ориентиры](/resources/lean-analytics/23-saas-lines-in-the-sand/) | Карта при регистрации, churn |
| [24. Мобильное приложение: ориентиры](/resources/lean-analytics/24-mobile-app-lines-in-the-sand/) | Цена установки, launch rate |
| [25. Медиа-сайт: ориентиры](/resources/lean-analytics/25-media-site-lines-in-the-sand/) | CTR, engaged time |
| [26. UGC: ориентиры](/resources/lean-analytics/26-user-generated-content-lines-in-the-sand/) | Загрузка, Reddit, модерация |
| [27. Маркетплейсы: ориентиры](/resources/lean-analytics/27-two-sided-marketplaces-lines-in-the-sand/) | Кейс Etsy |

### Часть IV. Внедрение

| Глава | Тема |
|---|---|
| [28. Нет базы для сравнения](/resources/lean-analytics/28-what-to-do-without-a-baseline/) | Убывающая отдача |
| [29. Продажи в enterprise](/resources/lean-analytics/29-selling-into-enterprise-markets/) | B2B и длинные циклы |
| [30. Интрапренёры](/resources/lean-analytics/30-lean-from-within-intrapreneurs/) | Lean внутри корпорации |
| [31. Заключение](/resources/lean-analytics/31-conclusion-beyond-startups/) | Культура данных |

## Связанные материалы

- [Книги](/resources/books/)
