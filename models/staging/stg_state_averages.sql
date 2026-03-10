{{
    config(
        materialized='view',
        schema='staging'
    )
}}

with source as (
    select * from {{ source('raw', 'state_averages') }}
),

renamed as (
    select
        state_or_nation as state,
        
        -- Staffing averages
        reported_total_nurse_staffing_hours_per_resident_per_day as avg_total_nursing_hprd,
        reported_rn_staffing_hours_per_resident_per_day as avg_rn_hprd,
        reported_lpn_staffing_hours_per_resident_per_day as avg_lpn_hprd,
        reported_nurse_aide_staffing_hours_per_resident_per_day as avg_cna_hprd,
        
        -- Turnover averages
        total_nursing_staff_turnover as avg_total_turnover_pct,
        registered_nurse_turnover as avg_rn_turnover_pct,
        
        -- Penalties
        number_of_fines as avg_fines_count,
        fine_amount_in_dollars as avg_fine_amount,
        
        processing_date,
        _load_time
        
    from source
)

select * from renamed