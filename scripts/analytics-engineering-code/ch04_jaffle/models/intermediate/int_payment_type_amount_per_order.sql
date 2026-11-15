-- intermediate: меняем grain с платежа на заказ
with order_payments as (
    select * from {{ ref('stg_stripe_order_payments') }}
)

select
    order_id,
    sum(case when payment_type = 'cash' and status = 'success'
             then amount else 0 end) as cash_amount,
    sum(case when payment_type = 'credit' and status = 'success'
             then amount else 0 end) as credit_amount,
    sum(case when status = 'success' then amount end) as total_amount
from order_payments
group by order_id
