-- analysis: dbt его компилирует, но не создаёт объект в базе
with fct_orders as (
    select * from {{ ref('fct_orders') }}
),

dim_customers as (
    select * from {{ ref('dim_customers') }}
)

select
    cust.customer_id,
    cust.first_name,
    sum(ord.total_amount) as global_paid_amount
from fct_orders as ord
left join dim_customers as cust
    on ord.customer_id = cust.customer_id
where ord.is_order_completed = 1
group by cust.customer_id, cust.first_name
order by global_paid_amount desc
limit 3
