-- models/marts/dim_products.sql
with stg_dim_products as (
    select
        product_sku  as nk_product_sku,
        product_name as dsc_product_name,
        unit_price   as mtr_unit_price,
        created_at   as dt_created_at,
        updated_at   as dt_updated_at
    from {{ ref('stg_products') }}
)
select
    {{ dbt_utils.generate_surrogate_key(['nk_product_sku']) }} as sk_product,
    *
from stg_dim_products
