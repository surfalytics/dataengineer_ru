---
title: Визуализация данных
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Визуализация данных: принципы и инструменты | Инжиниринг Данных"
description: "Визуализация данных: принципы, инструменты, книги и курсы для аналитиков и инженеров данных."
sidebar:
  order: 10
tags:
  - visualization
  - bi
---
Визуализация данных — это представление данных в виде графиков и диаграмм. Она делает сложную информацию понятной: числа и текст превращаются в картинки, которые проще читать и анализировать.
Для дата-инженера визуализация — не главный навык. Но она нужна всем, кто работает с данными, и помогает во многих задачах.

### Зачем данные визуализировать?
> 🇷🇺 / 🇬🇧 — язык материалов

Начните с того, зачем вообще нужна визуализация. Статьи на эту тему:
- [Зачем визуализировать данные?](https://nastengraph.substack.com/p/why-you-should-always-visualize-your)🇬🇧
- [Квартет Анскомбе](https://habr.com/ru/articles/91128/)🇷🇺
- [Same Stats, Different Graphs](https://www.research.autodesk.com/publications/same-stats-different-graphs/)🇬🇧
    
Следующий шаг — научиться подбирать график под ваши данные. Чаще всего хватает нескольких универсальных типов графиков:
- **Сравнение**: для вопросов вроде «В какой категории самые большие продажи?» лучше всего подойдут столбчатые диаграммы (барчарты).
- **Тренды и динамика**: если нужно показать изменения со временем, используйте линейный график. Например, он отвечает на вопрос: «Растут ли наши продажи с течением времени?». Линейные графики хорошо показывают непрерывные данные и тренды.
- **Часть от целого**: пайчарты и тримапы помогут ответить на вопросы вроде «Какой процент от общих продаж приходится на эту категорию?» Такие графики показывают, как отдельные части складываются в общий результат.
- **Связи**: для изучения взаимосвязей между переменными подойдут диаграммы рассеяния. Например, «Как связаны продажи и прибыль?» Эти графики помогают выявлять корреляции и выбросы в данных.
- **Распределение**: чтобы понять, как распределяются данные, используйте гистограммы или джиттер-плот (jitter plot). Например, можно ответить на вопрос: «Как распределяется пожизненная ценность клиента (LTV)?». Гистограммы покажут частоту значений, а джиттер-плот покажет каждое наблюдение отдельно.
- **Быстрый обзор**: для оперативного анализа подойдут KPI-карточки (также известны как фактоиды, BANы) с небольшими графиками — спарклайнами. Они дают краткий обзор ключевых метрик и отвечают на такие вопросы, как «Какие у нас текущие продажи?».
- **Точные значения**: для отображения конкретных данных таблицы остаются лучшим выбором. Добавьте к ним визуальные элементы вроде тепловых карт или спарклайнов. Так таблица ответит на вопрос вроде «Какие точные показатели продаж по регионам и категориям?».

### Подборка ресурсов для выбора графиков:
- [Чартчузер Александра Богачева](https://t.me/chartomojka/1259)🇷🇺
- [Dataviz Catalogue](https://datavizcatalogue.com/blog/chart-snapshot-dumbbell-plot/#google_vignette)🇬🇧🇷🇺
- [from data to viz](https://www.data-to-viz.com)🇬🇧 + есть примеры кода на R, Python, d3js
- [Financial Times Visual Vocabulary](https://github.com/Financial-Times/chart-doctor/blob/main/visual-vocabulary/README.md)🇬🇧
- [Dataviz project](https://datavizproject.com)🇬🇧

90% задач можно эффективно решить, используя всего два типа графиков — барчарты и линейные графики:

**Барчарты** подходят для сравнения категорий и отображения рейтингов. Например, можно сравнить продажи в разных регионах или показать распределение по категориям. 
**Линейные графики** хорошо показывают изменения во времени. Они помогают увидеть, как показатели, например, доход или трафик сайта, меняются на протяжении периода. 
Научитесь строить эти два типа графиков без самых частых ошибок: 
- [Правила к барчартам](https://nastengraph.substack.com/p/bar-charts-best-practices)🇬🇧
- [Правила к линейным графикам](https://nastengraph.substack.com/p/line-charts-best-practices)🇬🇧

### Где создавать графики?

- Кодом
  - Python: matplotlib, seaborn, plotnine, plotly. Варианты и код можно посмотреть на [python graph gallery](https://python-graph-gallery.com) 
  - R: ggplot2, plotly. Варианты и код можно посмотреть на [r graph gallery](https://r-graph-gallery.com)
  - D3.js. Варианты и код можно посмотреть на [d3 graph gallery](https://d3-graph-gallery.com)

- BI-инструменты (для графиков и дашбордов по ним)
  - [Yandex DataLens](https://yandex.cloud/en/services/datalens) — облачный и бесплатный
  - [Tableau](https://www.tableau.com) — есть бесплатная версия Tableau Public
  - [Power BI](https://www.microsoft.com/en-us/power-platform/products/power-bi)
  - [Looker & Looker Studio](https://www.google.com/search?client=safari&rls=en&q=looker+studio&ie=UTF-8&oe=UTF-8)

- Онлайн
  - [Datawrapper](https://www.datawrapper.de)
  - [RAWGraphs](https://rawgraphs.io)
  - [Flourish](https://flourish.studio)

### Что почитать?
- [«Графики, которые убеждают всех», Александр Богачев](https://www.ozon.ru/product/grafiki-kotorye-ubezhdayut-vseh-2-e-dopolnennoe-i-pererabotannoe-izdanie-bogachev-1383550700/?asb=p5PxqYT9%252FktCyJwzoS7hgvMjCC07V%252Bm14BXIZ5%252F%252B48E%253D&asb2=9FMngIroklXmLTbdVFb9jYtwcYJH4xvxUjUJoWJehOn8Oi0sWzM4YVE2Y6yXxI2t&avtc=1&avte=2&avts=1713081061&keywords=%D0%93%D1%80%D0%B0%D1%84%D0%B8%D0%BA%D0%B8%2C+%D0%BA%D0%BE%D1%82%D0%BE%D1%80%D1%8B%D0%B5+%D1%83%D0%B1%D0%B5%D0%B6%D0%B4%D0%B0%D1%8E%D1%82+%D0%B2%D1%81%D0%B5%D1%85+%7C+%D0%91%D0%BE%D0%B3%D0%B0%D1%87%D0%B5%D0%B2+%D0%90%D0%BB%D0%B5%D0%BA%D1%81%D0%B0%D0%BD%D0%B4%D1%80+%D0%90%D0%BD%D0%B4%D1%80%D0%B5%D0%B5%D0%B2%D0%B8%D1%87)🇷🇺
- [«Графики лгут. Как стать информационно грамотным человеком в мире данных?», Альберто Кайро](https://www.labirint.ru/books/857843/)🇷🇺
- [«Storytelling with Data», Cole Nussbaumer Knaflic](https://www.amazon.com/Storytelling-Data-Visualization-Business-Professionals/dp/1119002257)🇬🇧
- [«Fundamentals of Data Visualization», Claus O Wilke](https://clauswilke.com/dataviz/) 🇬🇧 — бесплатная открытая книга
- [«The Big Book of Dashboards: Visualizing Your Data Using Real-World Business Scenarios», Steve Wexler, Jeffrey Shaffer, Andy Cotgreave](https://www.amazon.ca/Big-Book-Dashboards-Visualizing-Real-World/dp/1119282713)🇬🇧

В телеграме — [папка каналов про датавиз](https://t.me/addlist/R_JRxzYACI41ZGRi)🇷🇺


