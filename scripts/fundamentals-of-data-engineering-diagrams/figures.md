# Рисунки: Fundamentals of Data Engineering

Только главы 8–11 (переписаны 2026-11-16). Главы 1–7 рисовали раньше, без списка.

| Глава | Figure | Идея | Наш файл | Статус |
|---|---|---|---|---|
| 8 | 8-1 | Transformations создают ценность из данных | — | skipped: декоративная схема |
| 8 | 8-2 | Жизнь SQL-запроса | ch08-query-life.png | redrawn (плюс способы ускорения) |
| 8 | 8-3 | CDC и fast follower | — | skipped: описано в тексте, схема есть в главе 7 |
| 8 | 8-4 | Kappa-архитектура | — | skipped: идея принадлежит главе 3, дана ссылка |
| 8 | 8-5, 8-6, 8-7, 8-8 | Session, fixed, sliding windows, watermark | ch08-stream-windows.png | redrawn (одна схема) |
| 8 | 8-9, 8-10, 8-11 | Join потоков, enrichment, stream-to-stream | — | skipped: в тексте |
| 8 | 8-12 | Conceptual, logical, physical | — | skipped: таблица на странице |
| 8 | 8-13, 8-14, 8-15, 8-16 | Inmon, Kimball, Data Vault | ch08-modeling-choice.png | redrawn (сравнение путей данных) |
| 8 | 8-17, 8-18 | Broadcast и shuffle hash join | ch08-joins.png | redrawn |
| 8 | 8-19, 8-20, 8-21 | Federated query, streaming DAG | — | skipped: в тексте |
| 8 | own | Update patterns | ch08-update-patterns.png | own |
| 9 | 9-1 Serving delivers data for use cases | Три сценария выдачи и общая основа | ch09-use-cases.png | redrawn |
| 9 | 9-2 Operational analytics dashboard | Скриншот дашборда Google Compute Engine | — | skipped: скриншот |
| 9 | 9-3 Federated query with three sources | Один запрос через движок к трём источникам | ch09-federation.png | redrawn |
| 9 | 9-4 Notebook served from many sources | Источники notebook | ch09-notebooks.png | redrawn (плюс наш путь масштабирования) |
| 9 | 9-5 Reverse ETL | Возврат данных в источник | ch09-reverse-etl.png | redrawn (на примере lead scoring, плюс риск feedback loop) |
| 9 | 9-6 Build, learn, improve | Петля обратной связи | — | skipped: декоративная, идея в тексте |
| 9 | own | Способы выдачи и когда подходят | ch09-ways-to-serve.png | own |
| 10 | — (в книге нет рисунков) | Люди, процессы, технологии и главный риск каждого уровня | ch10-security-layers.png | own, redrawn from text |
| 10 | — | Least privilege и broken glass | ch10-least-privilege.png | own |
| 10 | — | Где работает шифрование и что оно не закрывает | ch10-encryption.png | own |
| 10 | — | Четыре области мониторинга, dashboard, alerts, план реакции | ch10-monitoring.png | own |
| 11 | Figure 11-1 | Live data stack: данные и ML идут между приложением и системами в реальном времени | ch11-mds-to-live.png | redrawn (рядом с MDS) |
| 11 | наша | Тренды: что надёжно, что спекуляция | ch11-trends.png | own |
| 11 | наша | Аналогия: ОС и cloud-scale data OS | ch11-data-os.png | own |
| 11 | наша | ELT против STL | ch11-stl.png | own |
