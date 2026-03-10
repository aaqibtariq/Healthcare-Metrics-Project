{{
    config(
        materialized='view',
        schema='intermediate'
    )
}}

with quality_scores as (
    select * from {{ ref('int_facility_quality_scores') }}
),

state_benchmarks as (
    select * from {{ ref('stg_state_averages') }}
),

with_benchmarks as (
    select
        q.*,
        b.avg_total_nursing_hprd as state_avg_nursing_hprd,
        b.avg_total_turnover_pct as state_avg_turnover_pct
    from quality_scores q
    left join state_benchmarks b on q.state = b.state
),

risk_scores as (
    select
        *,
        
        -- Risk factor 1: Low staffing (below state average)
        case 
            when reported_total_nursing_hprd < state_avg_nursing_hprd * 0.8 then 1 
            else 0 
        end as risk_low_staffing,
        
        -- Risk factor 2: High turnover (above state average)
        case 
            when total_nurse_turnover_pct > state_avg_turnover_pct * 1.2 then 1 
            else 0 
        end as risk_high_turnover,
        
        -- Risk factor 3: Low overall rating
        case 
            when overall_rating <= 2 then 1 
            else 0 
        end as risk_low_rating,
        
        -- Risk factor 4: High penalties
        case 
            when total_penalties >= 3 then 1 
            else 0 
        end as risk_high_penalties,
        
        -- Risk factor 5: High readmission rate
        case 
            when readmission_rate_short_stay > 25 then 1 
            else 0 
        end as risk_high_readmissions,
        
        -- Risk factor 6: Abuse deficiencies
        case 
            when abuse_deficiencies > 0 then 1 
            else 0 
        end as risk_abuse_deficiencies
        
    from with_benchmarks
)

select 
    *,
    -- Calculate total risk score (0-6)
    risk_low_staffing + 
    risk_high_turnover + 
    risk_low_rating + 
    risk_high_penalties + 
    risk_high_readmissions + 
    risk_abuse_deficiencies as total_risk_score,
    
    -- Risk category
    case 
        when (risk_low_staffing + risk_high_turnover + risk_low_rating + 
              risk_high_penalties + risk_high_readmissions + risk_abuse_deficiencies) >= 4 
        then 'Critical Risk'
        when (risk_low_staffing + risk_high_turnover + risk_low_rating + 
              risk_high_penalties + risk_high_readmissions + risk_abuse_deficiencies) >= 3 
        then 'High Risk'
        when (risk_low_staffing + risk_high_turnover + risk_low_rating + 
              risk_high_penalties + risk_high_readmissions + risk_abuse_deficiencies) >= 2 
        then 'Medium Risk'
        when (risk_low_staffing + risk_high_turnover + risk_low_rating + 
              risk_high_penalties + risk_high_readmissions + risk_abuse_deficiencies) >= 1 
        then 'Low Risk'
        else 'Minimal Risk'
    end as risk_category,
    
    -- Intervention priority
    case 
        when (risk_low_staffing + risk_high_turnover + risk_low_rating + 
              risk_high_penalties + risk_high_readmissions + risk_abuse_deficiencies) >= 4 then 1
        when (risk_low_staffing + risk_high_turnover + risk_low_rating + 
              risk_high_penalties + risk_high_readmissions + risk_abuse_deficiencies) >= 3 then 2
        when (risk_low_staffing + risk_high_turnover + risk_low_rating + 
              risk_high_penalties + risk_high_readmissions + risk_abuse_deficiencies) >= 2 then 3
        else 4
    end as intervention_priority
    
from risk_scores