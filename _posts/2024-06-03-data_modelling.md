---
title: Моделирование Данных
author: Дата Инженеръ
date: 2024-06-03
category: hard-skills
layout: post
section: Обработка и аналитика
cover: ../assets/surf2.svg
---

## DWH по Кимбалл 

Подход Кимбалла определяет нисходящий, итеративный и гибкий подход к созданию хранилища, который подчёркивает быстрое получение бизнес-ценности за счёт создания специализированных витрин данных для удовлетворения конкретных потребностей пользователей в отчётности. 

**Ресурсы:**
- [DWH по Кимбаллу и Data Mesh](https://bigdataschool.ru/blog/kimball-dwh-and-data-mesh.html)
- [Building a Kimball Data Warehouse](https://www.sqlservercentral.com/articles/building-a-kimball-data-warehouse)
- [Что такое аналитические хранилища данных](https://www.youtube.com/watch?v=JuQCUGUWqgU&list=PLkcP_moW_BpPWPFzTXsHQIbL4OafJHZCm&index=2)

## DWH по Инмон

Модель Инмона выступает за нисходящий подход к проектированию хранилища данных. В его методологии особое внимание уделяется созданию централизованного хранилища данных на основе нормализованной модели данных.

**Ресурсы:**
- [Плейлист Data Warehousing and Modeling](https://youtube.com/playlist?list=PLlOuZAcnp6h4aJROJUb45z_y3hxo-MAnK&si=0KsA0MBH_4KI2dw2)
- [Bill Inmon / Building the Data Lakehouse](https://t.me/analyst_books/22)
- [Building the Data Warehouse / W.H. Inmon](https://www.r-5.org/files/books/computers/databases/warehouses/W_H_Inmon-Building_the_Data_Warehouse-EN.pdf)

## Data Vault 

Data Vault — это подход к моделированию данных, который фокусируется на гибкости, масштабируемости и аудите данных. Он использует три основных типа таблиц: хабы, линки и сателлиты.

*Хабы:* Представляют ключевые субъекты бизнеса (например, клиенты, продукты).

*Линки:* Представляют связи между хабами (например, заказы).

*Сателлиты:* Хранят атрибуты и исторические данные (атрибуты клиентов, продуктов, заказов)

**Ресурсы:**
- [Секреты построения Data Vault 2.0](https://habr.com/ru/companies/cinimex/articles/857084/)
- [Введение в Data Vault](https://habr.com/ru/articles/348188/)
- [Структура Data Vault](https://yandex.cloud/ru/docs/glossary/datavault)

## Anchor Modelling

Anchor Modelling предоставляет гибкий метод моделирования, подходящий для работы с постоянно растущими объемами данных, которые меняются по структуре или содержанию. Якорная модель включает следующие сущности:

*Якорь:* представляет собой сущность или событие, содержит суррогатные ключи, ссылку на источник и время добавления записи.

*Атрибут:* используется для моделирования свойств и характеристик якорей, содержит суррогатный ключ якоря, значение атрибута, ссылку на источник записи и время добавления записи.

*Связь:* моделирует отношения между якорями.

*Узел:* используется для моделирования общих свойств (состояния).

**Ресурсы:**
- [Снежинка, Data Vault, Anchor Modeling. Какая методология проектирования DWH подойдет для вашего бизнеса?](https://habr.com/ru/articles/786822/)
- [Data Vault Anchor Modeling](https://www.youtube.com/watch?v=IZw1cB1uDts)
- [Database design using Anchor Modeling](https://www.codecentric.de/wissens-hub/blog/agile-database-design-using-anchor-modeling)