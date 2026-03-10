{{
    config(
        materialized='view',
        schema='staging'
    )
}}

with source as (
    select * from {{ source('raw', 'vbp_performance') }}
),

renamed as (
    select
        ccn as facility_id,
        provider_name as facility_name,
        state,
        
        snf_vbp_program_ranking as vbp_ranking,
        
        -- Scores
        achievement_score,
        improvement_score,
        performance_score,
        incentive_payment_multiplier,
        
        -- Baseline and performance readmission rates
        baseline_period_fy2019_rsrr as baseline_readmission_rate,
        performance_period_fy2022_rsrr as performance_readmission_rate,
        
        _load_time
        
    from source
)

select * from renamed