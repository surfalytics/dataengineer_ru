select orders.order_id
from {{ ref('fct_orders') }} as orders
left join {{ ref('line_items') }} as items using (order_id)
where items.order_id is null
