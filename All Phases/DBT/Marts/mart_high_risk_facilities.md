```sql
{{
    config(
        materialized='table',
        schema='core'
    )
}}

-- METRIC 5: High-Risk Facility Identification

with risk_factors as (
    select * from {{ ref('int_facility_risk_factors') }}
),

final as (
    select
        facility_id,
        facility_name,
        state,
        
        -- Current state
        overall_rating,
        reported_total_nursing_hprd,
        total_nurse_turnover_pct,
        total_penalties,
        health_deficiencies,
        
        -- Risk factors (0 or 1 each)
        risk_low_staffing,
        risk_high_turnover,
        risk_low_rating,
        risk_high_penalties,
        risk_high_readmissions,
        risk_abuse_deficiencies,
        
        -- Total risk score (0-6)
        total_risk_score,
        risk_category,
        intervention_priority,
        
        -- Benchmarks
        state_avg_nursing_hprd,
        state_avg_turnover_pct
        
    from risk_factors
)

select * from final
order by total_risk_score desc, overall_rating asc

```
