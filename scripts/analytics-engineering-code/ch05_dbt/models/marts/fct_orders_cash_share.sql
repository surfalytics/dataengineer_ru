select
    order_id,
    cash_amount,
    total_amount,
    {{ dbt_utils.safe_divide('cash_amount', 'total_amount') }} as cash_share
from {{ ref('fct_orders') }}
