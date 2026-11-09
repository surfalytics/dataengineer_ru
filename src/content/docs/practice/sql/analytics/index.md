---
title: "Аналитические кейсы"
description: "Три кейса из работы аналитика на данных Yammer: падение вовлечённости, поиск в продукте, проверка A/B-теста."
sidebar:
  order: 0
  label: "Обзор уровня"
tags:
  - sql
  - practice
---

Третий уровень. Это не уроки по синтаксису. Это три задачи, как в работе аналитика.

Для каждого кейса сначала идёт задача, потом — разбор. Разбор спрятан. Откройте его, только когда попробовали сами.

<!-- erd:start -->
## Модель данных

<div class="erd not-content" data-pagefind-ignore>
<svg class="erd-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 567 522" width="567" height="522" role="img" aria-label="Модель данных кейсов: данные Yammer">
<path class="erd-link" d="M314 51 H282 V51 H250"/>
<text class="erd-card" x="304" y="46" text-anchor="middle">1</text>
<text class="erd-card" x="260" y="46" text-anchor="middle">N</text>
<path class="erd-link" d="M314 51 H291 V253 H250"/>
<text class="erd-card" x="304" y="46" text-anchor="middle">1</text>
<text class="erd-card" x="260" y="248" text-anchor="middle">N</text>
<path class="erd-link" d="M424 158 V198"/>
<text class="erd-card" x="436" y="171" text-anchor="middle">1</text>
<text class="erd-card" x="436" y="193" text-anchor="middle">N</text>
<g class="erd-table"><rect class="erd-box" x="14" y="14" width="236" height="162" rx="6"/>
<path class="erd-head" d="M14 42 V20 Q14 14 20 14 H244 Q250 14 250 20 V42 Z"/>
<text class="erd-title" x="26" y="32">tutorial.yammer_events</text>
<rect class="erd-keyrow" x="15" y="42" width="234" height="18"/>
<text class="erd-col erd-key" x="26" y="55">user_id</text>
<text class="erd-type" x="238" y="55" text-anchor="end">int</text>
<text class="erd-col" x="26" y="73">occurred_at</text>
<text class="erd-type" x="238" y="73" text-anchor="end">timestamp</text>
<text class="erd-col" x="26" y="91">event_type</text>
<text class="erd-type" x="238" y="91" text-anchor="end">text</text>
<text class="erd-col" x="26" y="109">event_name</text>
<text class="erd-type" x="238" y="109" text-anchor="end">text</text>
<text class="erd-col" x="26" y="127">location</text>
<text class="erd-type" x="238" y="127" text-anchor="end">text</text>
<text class="erd-col" x="26" y="145">device</text>
<text class="erd-type" x="238" y="145" text-anchor="end">text</text>
<text class="erd-col" x="26" y="163">user_type</text>
<text class="erd-type" x="238" y="163" text-anchor="end">int</text>
</g>
<g class="erd-table"><rect class="erd-box" x="14" y="216" width="236" height="108" rx="6"/>
<path class="erd-head" d="M14 244 V222 Q14 216 20 216 H244 Q250 216 250 222 V244 Z"/>
<text class="erd-title" x="26" y="234">tutorial.yammer_emails</text>
<rect class="erd-keyrow" x="15" y="244" width="234" height="18"/>
<text class="erd-col erd-key" x="26" y="257">user_id</text>
<text class="erd-type" x="238" y="257" text-anchor="end">int</text>
<text class="erd-col" x="26" y="275">occurred_at</text>
<text class="erd-type" x="238" y="275" text-anchor="end">timestamp</text>
<text class="erd-col" x="26" y="293">action</text>
<text class="erd-type" x="238" y="293" text-anchor="end">text</text>
<text class="erd-col" x="26" y="311">user_type</text>
<text class="erd-type" x="238" y="311" text-anchor="end">int</text>
</g>
<g class="erd-table"><rect class="erd-box" x="14" y="364" width="236" height="144" rx="6"/>
<path class="erd-head" d="M14 392 V370 Q14 364 20 364 H244 Q250 364 250 370 V392 Z"/>
<text class="erd-title" x="26" y="382">benn.dimension_rollup_periods</text>
<text class="erd-col" x="26" y="405">period_id</text>
<text class="erd-type" x="238" y="405" text-anchor="end">int</text>
<text class="erd-col" x="26" y="423">time_id</text>
<text class="erd-type" x="238" y="423" text-anchor="end">timestamp</text>
<text class="erd-col" x="26" y="441">pst_start</text>
<text class="erd-type" x="238" y="441" text-anchor="end">timestamp</text>
<text class="erd-col" x="26" y="459">pst_end</text>
<text class="erd-type" x="238" y="459" text-anchor="end">timestamp</text>
<text class="erd-col" x="26" y="477">utc_start</text>
<text class="erd-type" x="238" y="477" text-anchor="end">timestamp</text>
<text class="erd-col" x="26" y="495">utc_end</text>
<text class="erd-type" x="238" y="495" text-anchor="end">timestamp</text>
</g>
<g class="erd-table"><rect class="erd-box" x="314" y="14" width="221" height="144" rx="6"/>
<path class="erd-head" d="M314 42 V20 Q314 14 320 14 H529 Q535 14 535 20 V42 Z"/>
<text class="erd-title" x="326" y="32">tutorial.yammer_users</text>
<rect class="erd-keyrow" x="315" y="42" width="219" height="18"/>
<text class="erd-col erd-key" x="326" y="55">user_id</text>
<text class="erd-type" x="523" y="55" text-anchor="end">int</text>
<text class="erd-col" x="326" y="73">created_at</text>
<text class="erd-type" x="523" y="73" text-anchor="end">timestamp</text>
<text class="erd-col" x="326" y="91">company_id</text>
<text class="erd-type" x="523" y="91" text-anchor="end">int</text>
<text class="erd-col" x="326" y="109">language</text>
<text class="erd-type" x="523" y="109" text-anchor="end">text</text>
<text class="erd-col" x="326" y="127">activated_at</text>
<text class="erd-type" x="523" y="127" text-anchor="end">timestamp</text>
<text class="erd-col" x="326" y="145">state</text>
<text class="erd-type" x="523" y="145" text-anchor="end">text</text>
</g>
<g class="erd-table"><rect class="erd-box" x="314" y="198" width="221" height="144" rx="6"/>
<path class="erd-head" d="M314 226 V204 Q314 198 320 198 H529 Q535 198 535 204 V226 Z"/>
<text class="erd-title" x="326" y="216">tutorial.yammer_experiments</text>
<rect class="erd-keyrow" x="315" y="226" width="219" height="18"/>
<text class="erd-col erd-key" x="326" y="239">user_id</text>
<text class="erd-type" x="523" y="239" text-anchor="end">int</text>
<text class="erd-col" x="326" y="257">occurred_at</text>
<text class="erd-type" x="523" y="257" text-anchor="end">timestamp</text>
<text class="erd-col" x="326" y="275">experiment</text>
<text class="erd-type" x="523" y="275" text-anchor="end">text</text>
<text class="erd-col" x="326" y="293">experiment_group</text>
<text class="erd-type" x="523" y="293" text-anchor="end">text</text>
<text class="erd-col" x="326" y="311">location</text>
<text class="erd-type" x="523" y="311" text-anchor="end">text</text>
<text class="erd-col" x="326" y="329">device</text>
<text class="erd-type" x="523" y="329" text-anchor="end">text</text>
</g>
</svg>
</div>

**Как читать схему.** Линия — связь для `JOIN` по `user_id`: один пользователь, много событий, писем и участий в тестах. Выделенный столбец — ключ соединения. `dimension_rollup_periods` — справочник периодов, он соединяется по времени, а не по ключу.
<!-- erd:end -->

## Уроки

1. [Как работать с кейсами](/practice/sql/analytics/how-to/)
2. [Кейс 1: падение вовлечённости](/practice/sql/analytics/engagement-drop/)
3. [Кейс 1: разбор](/practice/sql/analytics/engagement-drop-answers/)
4. [Кейс 2: поиск в продукте](/practice/sql/analytics/search/)
5. [Кейс 2: разбор](/practice/sql/analytics/search-answers/)
6. [Кейс 3: проверка A/B-теста](/practice/sql/analytics/ab-test/)
7. [Кейс 3: разбор](/practice/sql/analytics/ab-test-answers/)
