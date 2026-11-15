-- staging: понятные имена и два простых признака
select
    id as payment_id,
    orderid as order_id,
    paymentmethod as payment_method,
    case
        when paymentmethod in ('credit_card', 'paypal', 'gift_card') then 'credit'
        else 'cash'
    end as payment_type,
    status,
    amount,
    status = 'success' as is_completed_payment,
    created as created_date
from {{ source('stripe', 'payment') }}
