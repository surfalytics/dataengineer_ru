select
    id as order_id,
    user_id as customer_id,
    order_date,
    status,
    _etl_loaded_at
from {{ source('jaffle_shop', 'orders') }}

{% if is_incremental() %}
-- при повторном запуске берём только новые и изменённые строки
where _etl_loaded_at >= (select max(_etl_loaded_at) from {{ this }})
{% endif %}
