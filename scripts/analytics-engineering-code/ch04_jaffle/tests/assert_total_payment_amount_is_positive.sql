-- singular test: падает, если запрос вернул хотя бы одну строку
select
    order_id,
    total_amount
from {{ ref('int_payment_type_amount_per_order') }}
where total_amount < 0
