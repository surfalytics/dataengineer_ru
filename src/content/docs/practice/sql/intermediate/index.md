---
title: "Средний уровень SQL"
description: "Второй уровень курса: агрегаты, GROUP BY, HAVING, CASE, DISTINCT, все виды JOIN, UNION. Задания на DuckDB."
sidebar:
  order: 0
  label: "Обзор уровня"
tags:
  - sql
  - practice
---

Второй уровень. Вы считаете агрегаты, группируете данные и соединяете таблицы.

Работаем с таблицами Crunchbase, акциями Apple и футболистами. Описание таблиц: [Учебные данные](/practice/sql/datasets/). Нужны знания из уровня [Основы](/practice/sql/basic/).

Решайте сами, без AI. Сначала задание, потом проверка, и только потом решение.

<!-- erd:start -->
## Модель данных

<div class="erd not-content" data-pagefind-ignore>
<svg class="erd-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 691 1016" width="691" height="1016" role="img" aria-label="Модель данных среднего уровня">
<path class="erd-view-link" d="M512 486 V526"/>
<path class="erd-view-link" d="M659 670 H673 V284 H659"/>
<path class="erd-link" d="M365 51 H333 V51 H301"/>
<text class="erd-card" x="355" y="46" text-anchor="middle">1</text>
<text class="erd-card" x="311" y="46" text-anchor="middle">N</text>
<path class="erd-link" d="M512 230 V270"/>
<text class="erd-card" x="524" y="243" text-anchor="middle">1</text>
<text class="erd-card" x="524" y="265" text-anchor="middle">N</text>
<path class="erd-link" d="M301 307 H324 V841 H365"/>
<text class="erd-card" x="311" y="302" text-anchor="middle">1</text>
<text class="erd-card" x="355" y="836" text-anchor="middle">N</text>
<g class="erd-table"><rect class="erd-box" x="14" y="14" width="287" height="180" rx="6"/>
<path class="erd-head" d="M14 42 V20 Q14 14 20 14 H295 Q301 14 301 20 V42 Z"/>
<text class="erd-title" x="26" y="32">tutorial.crunchbase_acquisitions</text>
<rect class="erd-keyrow" x="15" y="42" width="285" height="18"/>
<text class="erd-col erd-key" x="26" y="55">company_permalink</text>
<text class="erd-type" x="289" y="55" text-anchor="end">text</text>
<text class="erd-col" x="26" y="73">company_name</text>
<text class="erd-type" x="289" y="73" text-anchor="end">text</text>
<text class="erd-col" x="26" y="91">acquirer_name</text>
<text class="erd-type" x="289" y="91" text-anchor="end">text</text>
<text class="erd-col" x="26" y="109">acquired_at</text>
<text class="erd-type" x="289" y="109" text-anchor="end">text</text>
<text class="erd-col" x="26" y="127">acquired_year</text>
<text class="erd-type" x="289" y="127" text-anchor="end">bigint</text>
<text class="erd-col" x="26" y="145">price_amount</text>
<text class="erd-type" x="289" y="145" text-anchor="end">double</text>
<text class="erd-col" x="26" y="163">price_currency_code</text>
<text class="erd-type" x="289" y="163" text-anchor="end">text</text>
<text class="erd-note" x="26" y="181">… ещё 13 ст.</text>
</g>
<g class="erd-table"><rect class="erd-box" x="14" y="234" width="287" height="126" rx="6"/>
<path class="erd-head" d="M14 262 V240 Q14 234 20 234 H295 Q301 234 301 240 V262 Z"/>
<text class="erd-title" x="26" y="252">benn.college_football_teams</text>
<text class="erd-col" x="26" y="275">division</text>
<text class="erd-type" x="289" y="275" text-anchor="end">text</text>
<text class="erd-col" x="26" y="293">conference</text>
<text class="erd-type" x="289" y="293" text-anchor="end">text</text>
<rect class="erd-keyrow" x="15" y="298" width="285" height="18"/>
<text class="erd-col erd-key" x="26" y="311">school_name</text>
<text class="erd-type" x="289" y="311" text-anchor="end">text</text>
<text class="erd-col" x="26" y="329">roster_url</text>
<text class="erd-type" x="289" y="329" text-anchor="end">text</text>
<text class="erd-col" x="26" y="347">id</text>
<text class="erd-type" x="289" y="347" text-anchor="end">int</text>
</g>
<g class="erd-table"><rect class="erd-box" x="14" y="400" width="287" height="198" rx="6"/>
<path class="erd-head" d="M14 428 V406 Q14 400 20 400 H295 Q301 400 301 406 V428 Z"/>
<text class="erd-title" x="26" y="418">tutorial.aapl_historical_stock_price</text>
<text class="erd-col" x="26" y="441">date</text>
<text class="erd-type" x="289" y="441" text-anchor="end">date</text>
<text class="erd-col" x="26" y="459">year</text>
<text class="erd-type" x="289" y="459" text-anchor="end">int</text>
<text class="erd-col" x="26" y="477">month</text>
<text class="erd-type" x="289" y="477" text-anchor="end">int</text>
<text class="erd-col" x="26" y="495">open</text>
<text class="erd-type" x="289" y="495" text-anchor="end">double</text>
<text class="erd-col" x="26" y="513">high</text>
<text class="erd-type" x="289" y="513" text-anchor="end">double</text>
<text class="erd-col" x="26" y="531">low</text>
<text class="erd-type" x="289" y="531" text-anchor="end">double</text>
<text class="erd-col" x="26" y="549">close</text>
<text class="erd-type" x="289" y="549" text-anchor="end">double</text>
<text class="erd-col" x="26" y="567">volume</text>
<text class="erd-type" x="289" y="567" text-anchor="end">bigint</text>
<text class="erd-col" x="26" y="585">id</text>
<text class="erd-type" x="289" y="585" text-anchor="end">int</text>
</g>
<g class="erd-table"><rect class="erd-box" x="365" y="14" width="294" height="216" rx="6"/>
<path class="erd-head" d="M365 42 V20 Q365 14 371 14 H653 Q659 14 659 20 V42 Z"/>
<text class="erd-title" x="377" y="32">tutorial.crunchbase_companies</text>
<rect class="erd-keyrow" x="366" y="42" width="292" height="18"/>
<text class="erd-col erd-key" x="377" y="55">permalink</text>
<text class="erd-type" x="647" y="55" text-anchor="end">text</text>
<text class="erd-col" x="377" y="73">name</text>
<text class="erd-type" x="647" y="73" text-anchor="end">text</text>
<text class="erd-col" x="377" y="91">category_code</text>
<text class="erd-type" x="647" y="91" text-anchor="end">text</text>
<text class="erd-col" x="377" y="109">funding_total_usd</text>
<text class="erd-type" x="647" y="109" text-anchor="end">bigint</text>
<text class="erd-col" x="377" y="127">status</text>
<text class="erd-type" x="647" y="127" text-anchor="end">text</text>
<text class="erd-col" x="377" y="145">country_code</text>
<text class="erd-type" x="647" y="145" text-anchor="end">text</text>
<text class="erd-col" x="377" y="163">state_code</text>
<text class="erd-type" x="647" y="163" text-anchor="end">text</text>
<text class="erd-col" x="377" y="181">founded_at</text>
<text class="erd-type" x="647" y="181" text-anchor="end">text</text>
<text class="erd-col" x="377" y="199">founded_year</text>
<text class="erd-type" x="647" y="199" text-anchor="end">bigint</text>
<text class="erd-note" x="377" y="217">… ещё 8 ст.</text>
</g>
<g class="erd-table"><rect class="erd-box" x="365" y="270" width="294" height="216" rx="6"/>
<path class="erd-head" d="M365 298 V276 Q365 270 371 270 H653 Q659 270 659 276 V298 Z"/>
<text class="erd-title" x="377" y="288">tutorial.crunchbase_investments</text>
<rect class="erd-keyrow" x="366" y="298" width="292" height="18"/>
<text class="erd-col erd-key" x="377" y="311">company_permalink</text>
<text class="erd-type" x="647" y="311" text-anchor="end">text</text>
<text class="erd-col" x="377" y="329">company_name</text>
<text class="erd-type" x="647" y="329" text-anchor="end">text</text>
<text class="erd-col" x="377" y="347">investor_permalink</text>
<text class="erd-type" x="647" y="347" text-anchor="end">text</text>
<text class="erd-col" x="377" y="365">investor_name</text>
<text class="erd-type" x="647" y="365" text-anchor="end">text</text>
<text class="erd-col" x="377" y="383">investor_country_code</text>
<text class="erd-type" x="647" y="383" text-anchor="end">text</text>
<text class="erd-col" x="377" y="401">funding_round_type</text>
<text class="erd-type" x="647" y="401" text-anchor="end">text</text>
<text class="erd-col" x="377" y="419">funded_at</text>
<text class="erd-type" x="647" y="419" text-anchor="end">text</text>
<text class="erd-col" x="377" y="437">funded_year</text>
<text class="erd-type" x="647" y="437" text-anchor="end">bigint</text>
<text class="erd-col" x="377" y="455">raised_amount_usd</text>
<text class="erd-type" x="647" y="455" text-anchor="end">double</text>
<text class="erd-note" x="377" y="473">… ещё 11 ст.</text>
</g>
<g class="erd-table"><rect class="erd-box erd-view" x="365" y="526" width="294" height="90" rx="6"/>
<path class="erd-head" d="M365 554 V532 Q365 526 371 526 H653 Q659 526 659 532 V554 Z"/>
<text class="erd-title" x="377" y="544">tutorial.crunchbase_investments_part1</text>
<text class="erd-note" x="377" y="567">Компании A–L</text>
<text class="erd-note" x="377" y="585">Те же столбцы, что у</text>
<text class="erd-note" x="377" y="603">crunchbase_investments</text>
</g>
<g class="erd-table"><rect class="erd-box erd-view" x="365" y="656" width="294" height="90" rx="6"/>
<path class="erd-head" d="M365 684 V662 Q365 656 371 656 H653 Q659 656 659 662 V684 Z"/>
<text class="erd-title" x="377" y="674">tutorial.crunchbase_investments_part2</text>
<text class="erd-note" x="377" y="697">Компании M–Z</text>
<text class="erd-note" x="377" y="715">Те же столбцы, что у</text>
<text class="erd-note" x="377" y="733">crunchbase_investments</text>
</g>
<g class="erd-table"><rect class="erd-box" x="365" y="786" width="294" height="216" rx="6"/>
<path class="erd-head" d="M365 814 V792 Q365 786 371 786 H653 Q659 786 659 792 V814 Z"/>
<text class="erd-title" x="377" y="804">benn.college_football_players</text>
<text class="erd-col" x="377" y="827">full_school_name</text>
<text class="erd-type" x="647" y="827" text-anchor="end">text</text>
<rect class="erd-keyrow" x="366" y="832" width="292" height="18"/>
<text class="erd-col erd-key" x="377" y="845">school_name</text>
<text class="erd-type" x="647" y="845" text-anchor="end">text</text>
<text class="erd-col" x="377" y="863">player_name</text>
<text class="erd-type" x="647" y="863" text-anchor="end">text</text>
<text class="erd-col" x="377" y="881">position</text>
<text class="erd-type" x="647" y="881" text-anchor="end">text</text>
<text class="erd-col" x="377" y="899">height</text>
<text class="erd-type" x="647" y="899" text-anchor="end">int</text>
<text class="erd-col" x="377" y="917">weight</text>
<text class="erd-type" x="647" y="917" text-anchor="end">int</text>
<text class="erd-col" x="377" y="935">year</text>
<text class="erd-type" x="647" y="935" text-anchor="end">text</text>
<text class="erd-col" x="377" y="953">hometown</text>
<text class="erd-type" x="647" y="953" text-anchor="end">text</text>
<text class="erd-col" x="377" y="971">state</text>
<text class="erd-type" x="647" y="971" text-anchor="end">text</text>
<text class="erd-col" x="377" y="989">id</text>
<text class="erd-type" x="647" y="989" text-anchor="end">int</text>
</g>
</svg>
</div>

**Как читать схему.** Линия — связь для `JOIN`. Подписи `1` и `N` показывают, сколько строк с каждой стороны: у одной компании может быть много покупок и инвестиций. Выделенный столбец — ключ соединения. Пунктир — представление (view): часть данных другой таблицы. Таблицы без линий не связаны с остальными. Показаны главные столбцы широких таблиц. Полный список столбцов: [Учебные данные](/practice/sql/datasets/).
<!-- erd:end -->

## Уроки

1. [Агрегатные функции](/practice/sql/intermediate/aggregate-functions/)
2. [COUNT](/practice/sql/intermediate/count/)
3. [SUM](/practice/sql/intermediate/sum/)
4. [MIN и MAX](/practice/sql/intermediate/min-max/)
5. [AVG](/practice/sql/intermediate/avg/)
6. [GROUP BY](/practice/sql/intermediate/group-by/)
7. [HAVING](/practice/sql/intermediate/having/)
8. [CASE](/practice/sql/intermediate/case/)
9. [DISTINCT](/practice/sql/intermediate/distinct/)
10. [JOIN](/practice/sql/intermediate/joins/)
11. [INNER JOIN](/practice/sql/intermediate/inner-join/)
12. [Внешние соединения (OUTER JOIN)](/practice/sql/intermediate/outer-joins/)
13. [LEFT JOIN](/practice/sql/intermediate/left-join/)
14. [RIGHT JOIN](/practice/sql/intermediate/right-join/)
15. [Фильтр в WHERE или в ON](/practice/sql/intermediate/joins-where-vs-on/)
16. [FULL OUTER JOIN](/practice/sql/intermediate/full-outer-join/)
17. [UNION](/practice/sql/intermediate/union/)
18. [JOIN с операторами сравнения](/practice/sql/intermediate/join-comparison-operators/)
19. [JOIN по нескольким ключам](/practice/sql/intermediate/joins-on-multiple-keys/)
20. [Self JOIN](/practice/sql/intermediate/self-joins/)
