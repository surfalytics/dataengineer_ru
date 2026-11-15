with stg_dim_channels as (
    select
        channel_id   as nk_channel_id,
        channel_name as dsc_channel_name,
        created_at   as dt_created_at,
        updated_at   as dt_updated_at
    from {{ ref('stg_channels') }}
)
select
    {{ dbt_utils.generate_surrogate_key(['nk_channel_id']) }} as sk_channel,
    *
from stg_dim_channels
