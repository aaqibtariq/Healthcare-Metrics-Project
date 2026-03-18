```sql

{{
    config(
        materialized='view',
        schema='staging'
    )
}}

with source as (
    select * from {{ source('raw', 'penalties') }}
),

renamed as (
    select
        ccn as facility_id,
        provider_name as facility_name,
        state,
        
        penalty_date,
        penalty_type,
        fine_amount,
        payment_denial_start_date,
        payment_denial_length_in_days,
        
        processing_date,
        _load_time
        
    from source
)

select * from renamed

```
