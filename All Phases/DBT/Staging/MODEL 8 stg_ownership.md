```sql

{{
    config(
        materialized='view',
        schema='staging'
    )
}}

with source as (
    select * from {{ source('raw', 'ownership') }}
),

renamed as (
    select
        ccn as facility_id,
        provider_name as facility_name,
        
        role_played_by_owner_or_manager_in_facility as owner_role,
        owner_type,
        owner_name,
        ownership_percentage,
        association_date,
        
        processing_date,
        _load_time
        
    from source
)

select * from renamed


```
