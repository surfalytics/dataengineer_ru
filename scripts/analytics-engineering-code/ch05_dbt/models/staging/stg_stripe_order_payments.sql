select
    id as payment_id,
    order_id,
    payment_method,
    payment_type,
    status,
    amount
from {{ source('stripe', 'payments') }}
