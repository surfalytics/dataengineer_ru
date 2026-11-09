---
title: "Основы SQL"
description: "Первый уровень курса: SELECT, WHERE, операторы сравнения, LIKE, IN, BETWEEN, IS NULL, AND, OR, NOT, ORDER BY. Задания на DuckDB."
sidebar:
  order: 0
  label: "Обзор уровня"
tags:
  - sql
  - practice
---

Первый уровень. Вы учитесь выбирать и фильтровать данные из таблицы.

Работаем с таблицами `tutorial.us_housing_units` и `tutorial.billboard_top_100_year_end`. Описание таблиц: [Учебные данные](/practice/sql/datasets/). Не установили DuckDB? Начните с [установки](/practice/sql/setup/).

Идите по урокам по порядку. Каждый урок: пример, потом задания. Решайте сами, без AI.

<!-- erd:start -->
## Модель данных

<div class="erd not-content" data-pagefind-ignore>
<svg class="erd-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 625 446" width="625" height="446" role="img" aria-label="Модель данных уровня «Основы»: три таблицы без связей">
<g class="erd-table"><rect class="erd-box" x="14" y="14" width="236" height="162" rx="6"/>
<path class="erd-head" d="M14 42 V20 Q14 14 20 14 H244 Q250 14 250 20 V42 Z"/>
<text class="erd-title" x="26" y="32">tutorial.us_housing_units</text>
<text class="erd-col" x="26" y="55">year</text>
<text class="erd-type" x="238" y="55" text-anchor="end">int</text>
<text class="erd-col" x="26" y="73">month</text>
<text class="erd-type" x="238" y="73" text-anchor="end">int</text>
<text class="erd-col" x="26" y="91">month_name</text>
<text class="erd-type" x="238" y="91" text-anchor="end">text</text>
<text class="erd-col" x="26" y="109">south</text>
<text class="erd-type" x="238" y="109" text-anchor="end">double</text>
<text class="erd-col" x="26" y="127">west</text>
<text class="erd-type" x="238" y="127" text-anchor="end">double</text>
<text class="erd-col" x="26" y="145">midwest</text>
<text class="erd-type" x="238" y="145" text-anchor="end">double</text>
<text class="erd-col" x="26" y="163">northeast</text>
<text class="erd-type" x="238" y="163" text-anchor="end">double</text>
</g>
<g class="erd-table"><rect class="erd-box" x="14" y="216" width="236" height="216" rx="6"/>
<path class="erd-head" d="M14 244 V222 Q14 216 20 216 H244 Q250 216 250 222 V244 Z"/>
<text class="erd-title" x="26" y="234">tutorial.crunchbase_companies</text>
<text class="erd-col" x="26" y="257">permalink</text>
<text class="erd-type" x="238" y="257" text-anchor="end">text</text>
<text class="erd-col" x="26" y="275">name</text>
<text class="erd-type" x="238" y="275" text-anchor="end">text</text>
<text class="erd-col" x="26" y="293">category_code</text>
<text class="erd-type" x="238" y="293" text-anchor="end">text</text>
<text class="erd-col" x="26" y="311">funding_total_usd</text>
<text class="erd-type" x="238" y="311" text-anchor="end">bigint</text>
<text class="erd-col" x="26" y="329">status</text>
<text class="erd-type" x="238" y="329" text-anchor="end">text</text>
<text class="erd-col" x="26" y="347">country_code</text>
<text class="erd-type" x="238" y="347" text-anchor="end">text</text>
<text class="erd-col" x="26" y="365">state_code</text>
<text class="erd-type" x="238" y="365" text-anchor="end">text</text>
<text class="erd-col" x="26" y="383">founded_at</text>
<text class="erd-type" x="238" y="383" text-anchor="end">text</text>
<text class="erd-col" x="26" y="401">founded_year</text>
<text class="erd-type" x="238" y="401" text-anchor="end">bigint</text>
<text class="erd-note" x="26" y="419">… ещё 8 ст.</text>
</g>
<g class="erd-table"><rect class="erd-box" x="314" y="14" width="280" height="144" rx="6"/>
<path class="erd-head" d="M314 42 V20 Q314 14 320 14 H587 Q593 14 593 20 V42 Z"/>
<text class="erd-title" x="326" y="32">tutorial.billboard_top_100_year_end</text>
<text class="erd-col" x="326" y="55">year</text>
<text class="erd-type" x="581" y="55" text-anchor="end">int</text>
<text class="erd-col" x="326" y="73">year_rank</text>
<text class="erd-type" x="581" y="73" text-anchor="end">int</text>
<text class="erd-col" x="326" y="91">group_name</text>
<text class="erd-type" x="581" y="91" text-anchor="end">text</text>
<text class="erd-col" x="326" y="109">artist</text>
<text class="erd-type" x="581" y="109" text-anchor="end">text</text>
<text class="erd-col" x="326" y="127">song_name</text>
<text class="erd-type" x="581" y="127" text-anchor="end">text</text>
<text class="erd-col" x="326" y="145">id</text>
<text class="erd-type" x="581" y="145" text-anchor="end">int</text>
</g>
</svg>
</div>

Таблицы этого уровня не связаны друг с другом. Показаны главные столбцы широких таблиц. Полный список столбцов: [Учебные данные](/practice/sql/datasets/).
<!-- erd:end -->

## Уроки

1. [SELECT и FROM](/practice/sql/basic/select/)
2. [LIMIT](/practice/sql/basic/limit/)
3. [WHERE](/practice/sql/basic/where/)
4. [Операторы сравнения](/practice/sql/basic/comparison-operators/)
5. [Логические операторы](/practice/sql/basic/logical-operators/)
6. [LIKE](/practice/sql/basic/like/)
7. [IN](/practice/sql/basic/in/)
8. [BETWEEN](/practice/sql/basic/between/)
9. [IS NULL](/practice/sql/basic/is-null/)
10. [AND](/practice/sql/basic/and/)
11. [OR](/practice/sql/basic/or/)
12. [NOT](/practice/sql/basic/not/)
13. [ORDER BY](/practice/sql/basic/order-by/)
