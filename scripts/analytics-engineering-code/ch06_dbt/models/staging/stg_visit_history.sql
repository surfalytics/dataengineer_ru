with raw_visit_history as (
    select customer_id, channel_id, visit_timestamp, bounce_timestamp
    from {{ source('omnichannel', 'VisitHistory') }}
)
select * from raw_visit_history
