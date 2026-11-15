with customers as (
    select * from {{ ref('stg_jaffle_shop_customers') }}
)

select
    customer_id,
    first_name,
    last_name
from customers
