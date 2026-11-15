with raw_customers as (
    select customer_id, name, email_address, created_at, updated_at
    from {{ source('omnichannel', 'Customers') }}
)
select * from raw_customers
