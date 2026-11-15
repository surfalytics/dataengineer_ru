{{ config(materialized='table') }}

-- общая выручка: сумма по всем заказам
select
    sum(orders.revenue) as total_revenue,
    count(*)            as orders_cnt
from {{ ref('orders') }} as orders
