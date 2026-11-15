with fct_orders as (
    select * from {{ ref('fct_orders') }}
),

total_per_customer as (
    select
        customer_id,
        sum(total_amount) as global_paid_amount
    from fct_orders
    where is_order_completed = 1
    group by customer_id
),

ranges as (
    select * from {{ ref('seed_customer_range_per_paid_amount') }}
)

select
    t.customer_id,
    t.global_paid_amount,
    r.classification
from total_per_customer as t
left join ranges as r
    on t.global_paid_amount >= r.min_range
   and t.global_paid_amount < r.max_range
order by t.customer_id
