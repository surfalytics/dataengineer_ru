---
title: Lean Analytics — конспект книги
head:
  - tag: title
    content: "Lean Analytics: конспект книги на русском | Инжиниринг Данных"
description: "Конспект книги Lean Analytics на русском. Зачем читать, как измерять стартап, метрики по бизнес-моделям и этапам, разбор по главам."
author: "Alistair Croll, Benjamin Yoskovitz"
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

📥 [Скачать конспект в EPUB](/downloads/lean-analytics.epub) — для телефона и электронной книги.

## Зачем нужна эта книга

Дата-инженер строит `pipeline` и витрины. Но данные нужны не сами по себе. Они нужны, чтобы бизнес принимал решения. Эта книга учит понимать, **какие данные нужны бизнесу и почему**.

- **Язык бизнеса.** Вы поймёте, что такое `churn`, `LTV`, `CAC`, `retention` и откуда они берутся.
- **Правильные метрики.** Вы отличите полезную метрику от «метрики для красоты» (vanity metric).
- **Домены.** Книга разбирает шесть бизнес-моделей: e-commerce, SaaS, мобильное приложение, медиа, пользовательский контент, маркетплейс. Для каждой есть свои ключевые метрики.
- **Этапы продукта.** Метрики зависят от этапа: от поиска проблемы до масштаба.
- **Ориентиры.** Книга даёт примерные «нормальные» значения метрик, чтобы понимать, хорошо вам или плохо.
- **Лучшие требования к данным.** Когда вы понимаете, зачем метрика, вы делаете модель данных точнее. Вы задаёте аналитику и продукту правильные вопросы.

## Для кого

| Роль | Что получит |
|---|---|
| Дата-инженер | Понимание, какие события и таблицы нужны для метрик продукта |
| Аналитик, BI-разработчик | Рамки для выбора метрик и объяснения их бизнесу |
| Продакт, маркетолог | Метод проверки гипотез без догадок |
| Основатель, инвестор | Способ оценить стартап по цифрам |
| `Intrapreneur` в большой компании | Применение Lean внутри корпорации |

Книга писалась про веб-стартапы. Но подходы работают и в локальном бизнесе, B2B, политических кампаниях и внутри крупных компаний.

## Как устроена книга

Книга основана на интервью со ста с лишним основателями и инвесторами и на 30+ кейсах. В конце каждой главы есть вопросы для самопроверки.

| Часть | О чём | Главы книги |
|---|---|---|
| I. Основы | Lean Startup и аналитика, фреймворки | 1–5 |
| II. Lean Analytics на практике | Шесть бизнес-моделей, пять этапов, One Metric That Matters | 6–20 |
| III. Ориентиры | Что такое «нормально» для каждой модели | 21–27 |
| IV. Внедрение | Нет базы для сравнения, enterprise, `intrapreneur` | 28–31 |

## Разбор по главам

### Часть I. Основы

| Глава | Тема |
|---|---|
| [1. Мы все лжём](/book-summaries/business/lean-analytics/01-we-are-all-liars/) | Почему интуиции мало, цикл Lean, пример Airbnb |
| [2. Как вести счёт](/book-summaries/business/lean-analytics/02-how-to-keep-score/) | Хорошие метрики, типы метрик, vanity, цикл Lean Analytics |
| [3. Чем заняться в жизни](/book-summaries/business/lean-analytics/03-deciding-what-to-do/) | Выбор идеи, Lean Canvas |
| [4. Data-driven и data-informed](/book-summaries/business/lean-analytics/04-data-driven-vs-data-informed/) | Локальный максимум, девять советов по данным |
| [5. Аналитические фреймворки](/book-summaries/business/lean-analytics/05-analytics-frameworks/) | AARRR, Engines of Growth, пирамида Эллиса |

### Часть II. Lean Analytics на практике

| Глава | Тема |
|---|---|
| [6. Одна главная метрика](/book-summaries/business/lean-analytics/06-one-metric-that-matters/) | Одна главная метрика |
| [7. Какой у вас бизнес](/book-summaries/business/lean-analytics/07-what-business-are-you-in/) | Бизнес-модель и рычаги роста |
| [8. Модель 1 — e-commerce](/book-summaries/business/lean-analytics/08-ecommerce/) | Воронка, режимы отношений |
| [9. Модель 2 — SaaS](/book-summaries/business/lean-analytics/09-saas/) | Churn, CAC, LTV |
| [10. Модель 3 — бесплатное мобильное приложение](/book-summaries/business/lean-analytics/10-mobile-app/) | DAU, ARPU, монетизация |
| [11. Модель 4 — медиасайт](/book-summaries/business/lean-analytics/11-media-site/) | Аудитория, реклама, CTR |
| [12. Модель 5 — пользовательский контент](/book-summaries/business/lean-analytics/12-user-generated-content/) | Воронка вовлечения |
| [13. Модель 6 — двусторонние маркетплейсы](/book-summaries/business/lean-analytics/13-two-sided-marketplaces/) | Курица и яйцо, доверие |
| [14. На каком вы этапе](/book-summaries/business/lean-analytics/14-what-stage-are-you-at/) | Пять этапов |
| [15. Этап 1 — Empathy](/book-summaries/business/lean-analytics/15-stage-one-empathy/) | Интервью и проблема |
| [16. Этап 2 — Stickiness](/book-summaries/business/lean-analytics/16-stage-two-stickiness/) | Удержание, MVP |
| [17. Этап 3 — Virality](/book-summaries/business/lean-analytics/17-stage-three-virality/) | `Viral coefficient` |
| [18. Этап 4 — Revenue](/book-summaries/business/lean-analytics/18-stage-four-revenue/) | LTV и CAC |
| [19. Этап 5 — Scale](/book-summaries/business/lean-analytics/19-stage-five-scale/) | Каналы, Three-Threes |
| [20. Модель и этап задают метрику](/book-summaries/business/lean-analytics/20-model-and-stage-drive-the-metric/) | Выбор метрики |

### Часть III. Ориентиры

| Глава | Тема |
|---|---|
| [21. Достаточно ли хороши ваши метрики](/book-summaries/business/lean-analytics/21-am-i-good-enough/) | Что считать нормой |
| [22. E-commerce — ориентиры](/book-summaries/business/lean-analytics/22-ecommerce-lines-in-the-sand/) | Конверсия, брошенные корзины |
| [23. SaaS — ориентиры](/book-summaries/business/lean-analytics/23-saas-lines-in-the-sand/) | Карта при регистрации, churn |
| [24. Мобильное приложение — ориентиры](/book-summaries/business/lean-analytics/24-mobile-app-lines-in-the-sand/) | Цена установки, launch rate |
| [25. Медиасайт — ориентиры](/book-summaries/business/lean-analytics/25-media-site-lines-in-the-sand/) | CTR, engaged time |
| [26. Пользовательский контент — ориентиры](/book-summaries/business/lean-analytics/26-user-generated-content-lines-in-the-sand/) | Загрузка, Reddit, модерация |
| [27. Двусторонние маркетплейсы — ориентиры](/book-summaries/business/lean-analytics/27-two-sided-marketplaces-lines-in-the-sand/) | Кейс Etsy |

### Часть IV. Внедрение

| Глава | Тема |
|---|---|
| [28. Что делать, если нет ориентира](/book-summaries/business/lean-analytics/28-what-to-do-without-a-baseline/) | Убывающая отдача |
| [29. Продажи крупному бизнесу](/book-summaries/business/lean-analytics/29-selling-into-enterprise-markets/) | B2B и длинные циклы |
| [30. Lean внутри большой компании](/book-summaries/business/lean-analytics/30-lean-from-within-intrapreneurs/) | Lean внутри корпорации |
| [31. Заключение — за пределами стартапов](/book-summaries/business/lean-analytics/31-conclusion-beyond-startups/) | Культура данных |

## Связанные материалы

- [Книги](/resources/books/)
