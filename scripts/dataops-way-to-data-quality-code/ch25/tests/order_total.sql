select orders.order_id
from {{ ref('fct_orders') }} as orders
join {{ ref('line_items') }} as items using (order_id)
where orders.status = 'delivered'
group by orders.order_id, orders.amount
having abs(orders.amount - sum(items.amount)) > 0.01
