select
    order_id, customer_id, status, amount,
    current_date - cast(age_days as integer) as order_date
from {{ ref('order_feed') }}
