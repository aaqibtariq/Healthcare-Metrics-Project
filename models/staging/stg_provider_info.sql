{{
    config(
        materialized='view',
        schema='staging'
    )
}}

with source as (
    select * from {{ source('raw', 'provider_info') }}
),

renamed as (
    select
        -- IDs
        ccn as facility_id,
        provider_name as facility_name,
        provider_address as address,
        city_town as city,
        state,
        zip_code,
        
        -- Facility Details
        ownership_type,
        number_of_certified_beds as certified_beds,
        average_number_of_residents_per_day as avg_daily_census,
        provider_type,
        
        -- Star Ratings
        overall_rating,
        health_inspection_rating,
        qm_rating as quality_measure_rating,
        staffing_rating,
        
        -- Staffing Metrics (Reported)
        reported_total_nurse_staffing_hours_per_resident_per_day as reported_total_nursing_hprd,
        reported_rn_staffing_hours_per_resident_per_day as reported_rn_hprd,
        reported_lpn_staffing_hours_per_resident_per_day as reported_lpn_hprd,
        reported_nurse_aide_staffing_hours_per_resident_per_day as reported_cna_hprd,
        
        -- Turnover
        total_nursing_staff_turnover as total_nurse_turnover_pct,
        registered_nurse_turnover as rn_turnover_pct,
        number_of_administrators_who_have_left_the_nursing_home as admin_turnover_count,
        
        -- Penalties Summary
        number_of_fines,
        total_amount_of_fines_in_dollars as total_fines_amount,
        number_of_payment_denials,
        total_number_of_penalties,
        
        -- Survey Scores
        total_weighted_health_survey_score,
        number_of_substantiated_complaints,
        
        -- Geographic
        latitude,
        longitude,
        
        -- Metadata
        processing_date,
        _load_time
        
    from source
)

select * from renamed