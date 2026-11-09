---
title: "Продвинутый SQL"
# SEO-заголовок для поиска (вкладка браузера). H1 и сайдбар берут title.
head:
  - tag: title
    content: "Продвинутый SQL: оконные функции и не только | Инжиниринг Данных"
description: "Четвёртый уровень курса: типы данных, даты, чистка данных, строки, подзапросы, оконные функции, производительность, pivot."
sidebar:
  order: 0
  label: "Обзор уровня"
tags:
  - sql
  - practice
---

Четвёртый уровень. Вы чистите данные, пишете подзапросы и оконные функции, читаете план запроса.

Нужны знания из уровней [Основы](/practice/sql/basic/) и [Средний уровень](/practice/sql/intermediate/). Описание таблиц: [Учебные данные](/practice/sql/datasets/).

Решайте сами, без AI.

<!-- erd:start -->
## Модель данных

<div class="erd not-content" data-pagefind-ignore>
<svg class="erd-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 764 1640" width="764" height="1640" role="img" aria-label="Модель данных продвинутого уровня">
<path class="erd-view-link" d="M183 194 V234"/>
<path class="erd-view-link" d="M183 598 V638"/>
<path class="erd-view-link" d="M352 782 H366 V396 H352"/>
<path class="erd-view-link" d="M574 230 V270"/>
<path class="erd-view-link" d="M574 634 V674"/>
<path class="erd-link" d="M416 51 H384 V51 H352"/>
<text class="erd-card" x="406" y="46" text-anchor="middle">1</text>
<text class="erd-card" x="362" y="46" text-anchor="middle">N</text>
<path class="erd-link" d="M416 307 H393 V271 H352"/>
<text class="erd-card" x="406" y="302" text-anchor="middle">1</text>
<text class="erd-card" x="362" y="266" text-anchor="middle">N</text>
<path class="erd-link" d="M574 1370 V1410"/>
<text class="erd-card" x="586" y="1383" text-anchor="middle">1</text>
<text class="erd-card" x="586" y="1405" text-anchor="middle">N</text>
<g class="erd-table"><rect class="erd-box" x="14" y="14" width="338" height="180" rx="6"/>
<path class="erd-head" d="M14 42 V20 Q14 14 20 14 H346 Q352 14 352 20 V42 Z"/>
<text class="erd-title" x="26" y="32">tutorial.crunchbase_acquisitions</text>
<rect class="erd-keyrow" x="15" y="42" width="336" height="18"/>
<text class="erd-col erd-key" x="26" y="55">company_permalink</text>
<text class="erd-type" x="340" y="55" text-anchor="end">text</text>
<text class="erd-col" x="26" y="73">company_name</text>
<text class="erd-type" x="340" y="73" text-anchor="end">text</text>
<text class="erd-col" x="26" y="91">acquirer_name</text>
<text class="erd-type" x="340" y="91" text-anchor="end">text</text>
<text class="erd-col" x="26" y="109">acquired_at</text>
<text class="erd-type" x="340" y="109" text-anchor="end">text</text>
<text class="erd-col" x="26" y="127">acquired_year</text>
<text class="erd-type" x="340" y="127" text-anchor="end">bigint</text>
<text class="erd-col" x="26" y="145">price_amount</text>
<text class="erd-type" x="340" y="145" text-anchor="end">double</text>
<text class="erd-col" x="26" y="163">price_currency_code</text>
<text class="erd-type" x="340" y="163" text-anchor="end">text</text>
<text class="erd-note" x="26" y="181">… ещё 13 ст.</text>
</g>
<g class="erd-table"><rect class="erd-box erd-view" x="14" y="234" width="338" height="108" rx="6"/>
<path class="erd-head" d="M14 262 V240 Q14 234 20 234 H346 Q352 234 352 240 V262 Z"/>
<text class="erd-title" x="26" y="252">tutorial.crunchbase_acquisitions_clean_date</text>
<rect class="erd-keyrow" x="15" y="262" width="336" height="18"/>
<text class="erd-col erd-key" x="26" y="275">company_permalink</text>
<text class="erd-type" x="340" y="275" text-anchor="end">text</text>
<text class="erd-col" x="26" y="293">acquired_at</text>
<text class="erd-type" x="340" y="293" text-anchor="end">text</text>
<text class="erd-col" x="26" y="311">acquired_at_cleaned</text>
<text class="erd-type" x="340" y="311" text-anchor="end">timestamp</text>
<text class="erd-note" x="26" y="329">… ещё 18 ст.</text>
</g>
<g class="erd-table"><rect class="erd-box" x="14" y="382" width="338" height="216" rx="6"/>
<path class="erd-head" d="M14 410 V388 Q14 382 20 382 H346 Q352 382 352 388 V410 Z"/>
<text class="erd-title" x="26" y="400">tutorial.crunchbase_investments</text>
<text class="erd-col" x="26" y="423">company_permalink</text>
<text class="erd-type" x="340" y="423" text-anchor="end">text</text>
<text class="erd-col" x="26" y="441">company_name</text>
<text class="erd-type" x="340" y="441" text-anchor="end">text</text>
<text class="erd-col" x="26" y="459">investor_permalink</text>
<text class="erd-type" x="340" y="459" text-anchor="end">text</text>
<text class="erd-col" x="26" y="477">investor_name</text>
<text class="erd-type" x="340" y="477" text-anchor="end">text</text>
<text class="erd-col" x="26" y="495">investor_country_code</text>
<text class="erd-type" x="340" y="495" text-anchor="end">text</text>
<text class="erd-col" x="26" y="513">funding_round_type</text>
<text class="erd-type" x="340" y="513" text-anchor="end">text</text>
<text class="erd-col" x="26" y="531">funded_at</text>
<text class="erd-type" x="340" y="531" text-anchor="end">text</text>
<text class="erd-col" x="26" y="549">funded_year</text>
<text class="erd-type" x="340" y="549" text-anchor="end">bigint</text>
<text class="erd-col" x="26" y="567">raised_amount_usd</text>
<text class="erd-type" x="340" y="567" text-anchor="end">double</text>
<text class="erd-note" x="26" y="585">… ещё 11 ст.</text>
</g>
<g class="erd-table"><rect class="erd-box erd-view" x="14" y="638" width="338" height="90" rx="6"/>
<path class="erd-head" d="M14 666 V644 Q14 638 20 638 H346 Q352 638 352 644 V666 Z"/>
<text class="erd-title" x="26" y="656">tutorial.crunchbase_investments_part1</text>
<text class="erd-note" x="26" y="679">Компании A–L</text>
<text class="erd-note" x="26" y="697">Те же столбцы, что у</text>
<text class="erd-note" x="26" y="715">crunchbase_investments</text>
</g>
<g class="erd-table"><rect class="erd-box erd-view" x="14" y="768" width="338" height="90" rx="6"/>
<path class="erd-head" d="M14 796 V774 Q14 768 20 768 H346 Q352 768 352 774 V796 Z"/>
<text class="erd-title" x="26" y="786">tutorial.crunchbase_investments_part2</text>
<text class="erd-note" x="26" y="809">Компании M–Z</text>
<text class="erd-note" x="26" y="827">Те же столбцы, что у</text>
<text class="erd-note" x="26" y="845">crunchbase_investments</text>
</g>
<g class="erd-table"><rect class="erd-box" x="14" y="898" width="338" height="126" rx="6"/>
<path class="erd-head" d="M14 926 V904 Q14 898 20 898 H346 Q352 898 352 904 V926 Z"/>
<text class="erd-title" x="26" y="916">tutorial.worldwide_earthquakes</text>
<text class="erd-col" x="26" y="939">magnitude</text>
<text class="erd-type" x="340" y="939" text-anchor="end">text</text>
<text class="erd-col" x="26" y="957">year_2000</text>
<text class="erd-type" x="340" y="957" text-anchor="end">bigint</text>
<text class="erd-col" x="26" y="975">year_2001</text>
<text class="erd-type" x="340" y="975" text-anchor="end">bigint</text>
<text class="erd-col" x="26" y="993">year_2012</text>
<text class="erd-type" x="340" y="993" text-anchor="end">bigint</text>
<text class="erd-note" x="26" y="1011">… ещё 10 ст.</text>
</g>
<g class="erd-table"><rect class="erd-box" x="416" y="14" width="316" height="216" rx="6"/>
<path class="erd-head" d="M416 42 V20 Q416 14 422 14 H726 Q732 14 732 20 V42 Z"/>
<text class="erd-title" x="428" y="32">tutorial.crunchbase_companies</text>
<rect class="erd-keyrow" x="417" y="42" width="314" height="18"/>
<text class="erd-col erd-key" x="428" y="55">permalink</text>
<text class="erd-type" x="720" y="55" text-anchor="end">text</text>
<text class="erd-col" x="428" y="73">name</text>
<text class="erd-type" x="720" y="73" text-anchor="end">text</text>
<text class="erd-col" x="428" y="91">category_code</text>
<text class="erd-type" x="720" y="91" text-anchor="end">text</text>
<text class="erd-col" x="428" y="109">funding_total_usd</text>
<text class="erd-type" x="720" y="109" text-anchor="end">bigint</text>
<text class="erd-col" x="428" y="127">status</text>
<text class="erd-type" x="720" y="127" text-anchor="end">text</text>
<text class="erd-col" x="428" y="145">country_code</text>
<text class="erd-type" x="720" y="145" text-anchor="end">text</text>
<text class="erd-col" x="428" y="163">state_code</text>
<text class="erd-type" x="720" y="163" text-anchor="end">text</text>
<text class="erd-col" x="428" y="181">founded_at</text>
<text class="erd-type" x="720" y="181" text-anchor="end">text</text>
<text class="erd-col" x="428" y="199">founded_year</text>
<text class="erd-type" x="720" y="199" text-anchor="end">bigint</text>
<text class="erd-note" x="428" y="217">… ещё 8 ст.</text>
</g>
<g class="erd-table"><rect class="erd-box erd-view" x="416" y="270" width="316" height="108" rx="6"/>
<path class="erd-head" d="M416 298 V276 Q416 270 422 270 H726 Q732 270 732 276 V298 Z"/>
<text class="erd-title" x="428" y="288">tutorial.crunchbase_companies_clean_date</text>
<rect class="erd-keyrow" x="417" y="298" width="314" height="18"/>
<text class="erd-col erd-key" x="428" y="311">permalink</text>
<text class="erd-type" x="720" y="311" text-anchor="end">text</text>
<text class="erd-col" x="428" y="329">founded_at</text>
<text class="erd-type" x="720" y="329" text-anchor="end">text</text>
<text class="erd-col" x="428" y="347">founded_at_clean</text>
<text class="erd-type" x="720" y="347" text-anchor="end">text</text>
<text class="erd-note" x="428" y="365">… ещё 15 ст.</text>
</g>
<g class="erd-table"><rect class="erd-box" x="416" y="418" width="316" height="216" rx="6"/>
<path class="erd-head" d="M416 446 V424 Q416 418 422 418 H726 Q732 418 732 424 V446 Z"/>
<text class="erd-title" x="428" y="436">tutorial.sf_crime_incidents_2014_01</text>
<text class="erd-col" x="428" y="459">incidnt_num</text>
<text class="erd-type" x="720" y="459" text-anchor="end">bigint</text>
<text class="erd-col" x="428" y="477">category</text>
<text class="erd-type" x="720" y="477" text-anchor="end">text</text>
<text class="erd-col" x="428" y="495">descript</text>
<text class="erd-type" x="720" y="495" text-anchor="end">text</text>
<text class="erd-col" x="428" y="513">day_of_week</text>
<text class="erd-type" x="720" y="513" text-anchor="end">text</text>
<text class="erd-col" x="428" y="531">date</text>
<text class="erd-type" x="720" y="531" text-anchor="end">text</text>
<text class="erd-col" x="428" y="549">time</text>
<text class="erd-type" x="720" y="549" text-anchor="end">text</text>
<text class="erd-col" x="428" y="567">resolution</text>
<text class="erd-type" x="720" y="567" text-anchor="end">text</text>
<text class="erd-col" x="428" y="585">lon</text>
<text class="erd-type" x="720" y="585" text-anchor="end">double</text>
<text class="erd-col" x="428" y="603">lat</text>
<text class="erd-type" x="720" y="603" text-anchor="end">double</text>
<text class="erd-note" x="428" y="621">… ещё 4 ст.</text>
</g>
<g class="erd-table"><rect class="erd-box erd-view" x="416" y="674" width="316" height="126" rx="6"/>
<path class="erd-head" d="M416 702 V680 Q416 674 422 674 H726 Q732 674 732 680 V702 Z"/>
<text class="erd-title" x="428" y="692">tutorial.sf_crime_incidents_cleandate</text>
<text class="erd-col" x="428" y="715">incidnt_num</text>
<text class="erd-type" x="720" y="715" text-anchor="end">bigint</text>
<text class="erd-col" x="428" y="733">date</text>
<text class="erd-type" x="720" y="733" text-anchor="end">text</text>
<text class="erd-col" x="428" y="751">time</text>
<text class="erd-type" x="720" y="751" text-anchor="end">text</text>
<text class="erd-col" x="428" y="769">cleaned_date</text>
<text class="erd-type" x="720" y="769" text-anchor="end">timestamp</text>
<text class="erd-note" x="428" y="787">… ещё 10 ст.</text>
</g>
<g class="erd-table"><rect class="erd-box" x="416" y="840" width="316" height="198" rx="6"/>
<path class="erd-head" d="M416 868 V846 Q416 840 422 840 H726 Q732 840 732 846 V868 Z"/>
<text class="erd-title" x="428" y="858">tutorial.dc_bikeshare_q1_2012</text>
<text class="erd-col" x="428" y="881">duration_seconds</text>
<text class="erd-type" x="720" y="881" text-anchor="end">int</text>
<text class="erd-col" x="428" y="899">start_time</text>
<text class="erd-type" x="720" y="899" text-anchor="end">timestamp</text>
<text class="erd-col" x="428" y="917">start_station</text>
<text class="erd-type" x="720" y="917" text-anchor="end">text</text>
<text class="erd-col" x="428" y="935">start_terminal</text>
<text class="erd-type" x="720" y="935" text-anchor="end">int</text>
<text class="erd-col" x="428" y="953">end_time</text>
<text class="erd-type" x="720" y="953" text-anchor="end">timestamp</text>
<text class="erd-col" x="428" y="971">end_station</text>
<text class="erd-type" x="720" y="971" text-anchor="end">text</text>
<text class="erd-col" x="428" y="989">end_terminal</text>
<text class="erd-type" x="720" y="989" text-anchor="end">int</text>
<text class="erd-col" x="428" y="1007">rider_type</text>
<text class="erd-type" x="720" y="1007" text-anchor="end">text</text>
<text class="erd-note" x="428" y="1025">… ещё 3 ст.</text>
</g>
<g class="erd-table"><rect class="erd-box" x="416" y="1078" width="316" height="126" rx="6"/>
<path class="erd-head" d="M416 1106 V1084 Q416 1078 422 1078 H726 Q732 1078 732 1084 V1106 Z"/>
<text class="erd-title" x="428" y="1096">benn.sample_event_table</text>
<text class="erd-col" x="428" y="1119">event_id</text>
<text class="erd-type" x="720" y="1119" text-anchor="end">int</text>
<text class="erd-col" x="428" y="1137">user_id</text>
<text class="erd-type" x="720" y="1137" text-anchor="end">int</text>
<text class="erd-col" x="428" y="1155">event_date</text>
<text class="erd-type" x="720" y="1155" text-anchor="end">date</text>
<text class="erd-col" x="428" y="1173">event_name</text>
<text class="erd-type" x="720" y="1173" text-anchor="end">text</text>
<text class="erd-col" x="428" y="1191">device</text>
<text class="erd-type" x="720" y="1191" text-anchor="end">text</text>
</g>
<g class="erd-table"><rect class="erd-box" x="416" y="1244" width="316" height="126" rx="6"/>
<path class="erd-head" d="M416 1272 V1250 Q416 1244 422 1244 H726 Q732 1244 732 1250 V1272 Z"/>
<text class="erd-title" x="428" y="1262">benn.college_football_teams</text>
<text class="erd-col" x="428" y="1285">division</text>
<text class="erd-type" x="720" y="1285" text-anchor="end">text</text>
<text class="erd-col" x="428" y="1303">conference</text>
<text class="erd-type" x="720" y="1303" text-anchor="end">text</text>
<rect class="erd-keyrow" x="417" y="1308" width="314" height="18"/>
<text class="erd-col erd-key" x="428" y="1321">school_name</text>
<text class="erd-type" x="720" y="1321" text-anchor="end">text</text>
<text class="erd-col" x="428" y="1339">roster_url</text>
<text class="erd-type" x="720" y="1339" text-anchor="end">text</text>
<text class="erd-col" x="428" y="1357">id</text>
<text class="erd-type" x="720" y="1357" text-anchor="end">int</text>
</g>
<g class="erd-table"><rect class="erd-box" x="416" y="1410" width="316" height="216" rx="6"/>
<path class="erd-head" d="M416 1438 V1416 Q416 1410 422 1410 H726 Q732 1410 732 1416 V1438 Z"/>
<text class="erd-title" x="428" y="1428">benn.college_football_players</text>
<text class="erd-col" x="428" y="1451">full_school_name</text>
<text class="erd-type" x="720" y="1451" text-anchor="end">text</text>
<rect class="erd-keyrow" x="417" y="1456" width="314" height="18"/>
<text class="erd-col erd-key" x="428" y="1469">school_name</text>
<text class="erd-type" x="720" y="1469" text-anchor="end">text</text>
<text class="erd-col" x="428" y="1487">player_name</text>
<text class="erd-type" x="720" y="1487" text-anchor="end">text</text>
<text class="erd-col" x="428" y="1505">position</text>
<text class="erd-type" x="720" y="1505" text-anchor="end">text</text>
<text class="erd-col" x="428" y="1523">height</text>
<text class="erd-type" x="720" y="1523" text-anchor="end">int</text>
<text class="erd-col" x="428" y="1541">weight</text>
<text class="erd-type" x="720" y="1541" text-anchor="end">int</text>
<text class="erd-col" x="428" y="1559">year</text>
<text class="erd-type" x="720" y="1559" text-anchor="end">text</text>
<text class="erd-col" x="428" y="1577">hometown</text>
<text class="erd-type" x="720" y="1577" text-anchor="end">text</text>
<text class="erd-col" x="428" y="1595">state</text>
<text class="erd-type" x="720" y="1595" text-anchor="end">text</text>
<text class="erd-col" x="428" y="1613">id</text>
<text class="erd-type" x="720" y="1613" text-anchor="end">int</text>
</g>
</svg>
</div>

**Как читать схему.** Линия — связь для `JOIN`, подписи `1` и `N` — число строк с каждой стороны. Выделенный столбец — ключ соединения. Пунктир — представление (view): оно показывает часть данных основной таблицы. Таблицы без линий не связаны с остальными. Показаны главные столбцы широких таблиц. Полный список столбцов: [Учебные данные](/practice/sql/datasets/).
<!-- erd:end -->

## Уроки

1. [Типы данных](/practice/sql/advanced/data-types/)
2. [Формат дат и времени](/practice/sql/advanced/date-format/)
3. [Подготовка данных (data wrangling)](/practice/sql/advanced/data-wrangling/)
4. [Строковые функции](/practice/sql/advanced/string-functions/)
5. [Подзапросы](/practice/sql/advanced/subqueries/)
6. [Оконные функции](/practice/sql/advanced/window-functions/)
7. [Скорость запросов](/practice/sql/advanced/performance-tuning/)
8. [Сводные таблицы (PIVOT)](/practice/sql/advanced/pivot/)
