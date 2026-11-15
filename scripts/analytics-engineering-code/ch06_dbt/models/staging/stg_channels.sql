-- models/staging/stg_channels.sql
with raw_channels as (
    select channel_id, channel_name, created_at, updated_at
    from {{ source('omnichannel', 'Channels') }}
)
select * from raw_channels
