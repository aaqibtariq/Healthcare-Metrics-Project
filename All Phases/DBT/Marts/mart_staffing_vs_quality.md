```sql

{{
    config(
        materialized='table',
        schema='core'
    )
}}

-- METRIC 3: Staffing vs Quality Outcomes

with quality_scores as (
    select * from {{ ref('int_facility_quality_scores') }}
),

final as (
    select
        facility_id,
        facility_name,
        state,
        
        -- Staffing
        reported_total_nursing_hprd,
        reported_rn_hprd,
        
        -- Quality Ratings
        overall_rating,
        health_inspection_rating,
        quality_measure_rating,
        staffing_rating,
        
        -- Outcomes
        readmission_rate_short_stay,
        ed_visit_rate_short_stay,
        hospitalization_rate_long_stay,
        
        -- Issues
        total_penalties,
        total_fines,
        health_deficiencies,
        
        -- Composite quality score (already calculated)
        composite_quality_score,
        quality_tier,
        
        -- Staffing adequacy vs quality
        case 
            when reported_total_nursing_hprd >= 4.0 and overall_rating >= 4 
            then 'High Staffing, High Quality'
            when reported_total_nursing_hprd >= 4.0 and overall_rating < 4 
            then 'High Staffing, Low Quality'
            when reported_total_nursing_hprd < 4.0 and overall_rating >= 4 
            then 'Low Staffing, High Quality'
            else 'Low Staffing, Low Quality'
        end as staffing_quality_category
        
    from quality_scores
)

select * from final
order by composite_quality_score desc


```
