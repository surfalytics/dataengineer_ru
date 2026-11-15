with raw_products as (
    select product_sku, product_name, unit_price, created_at, updated_at
    from {{ source('omnichannel', 'Products') }}
)
select * from raw_products
