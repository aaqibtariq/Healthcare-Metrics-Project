{{
    config(
        materialized='view',
        schema='intermediate'
    )
}}

with facility_info as (
    select * from {{ ref('stg_provider_info') }}
),

quality_claims as (
    select * from {{ ref('stg_quality_claims') }}
),

penalties as (
    select 
        facility_id,
        count(*) as total_penalties_count,
        sum(fine_amount) as total_fines_amount,
        max(penalty_date) as most_recent_penalty_date
    from {{ ref('stg_penalties') }}
    group by facility_id
),

survey_summary as (
    select 
        facility_id,
        sum(total_number_of_health_deficiencies) as total_health_deficiencies,
        sum(abuse_neglect_deficiencies) as total_abuse_deficiencies,
        sum(infection_control_deficiencies) as total_infection_deficiencies
    from {{ ref('stg_survey_summary') }}
    group by facility_id
),

joined as (
    select
        -- Facility
        f.facility_id,
        f.facility_name,
        f.state,
        f.overall_rating,
        f.health_inspection_rating,
        f.quality_measure_rating,
        f.staffing_rating,
        
        -- Staffing metrics
        f.reported_total_nursing_hprd,
        f.reported_rn_hprd,
        f.total_nurse_turnover_pct,
        
        -- Quality outcomes
        q.readmission_rate_short_stay,
        q.ed_visit_rate_short_stay,
        q.hospitalization_rate_long_stay,
        
        -- Penalties
        coalesce(p.total_penalties_count, 0) as total_penalties,
        coalesce(p.total_fines_amount, 0) as total_fines,
        
        -- Deficiencies
        coalesce(s.total_health_deficiencies, 0) as health_deficiencies,
        coalesce(s.total_abuse_deficiencies, 0) as abuse_deficiencies,
        coalesce(s.total_infection_deficiencies, 0) as infection_deficiencies,
        
        -- Calculated composite quality score (0-100)
        (
            coalesce(f.overall_rating, 0) * 10 +
            coalesce(f.health_inspection_rating, 0) * 10 +
            coalesce(f.quality_measure_rating, 0) * 10 +
            coalesce(f.staffing_rating, 0) * 10 -
            least(coalesce(p.total_penalties_count, 0) * 2, 20) -
            least(coalesce(s.total_health_deficiencies, 0), 20)
        ) / 100.0 * 100 as composite_quality_score,
        
        -- Quality tier
        case 
            when f.overall_rating >= 4 then 'High Quality'
            when f.overall_rating >= 3 then 'Medium Quality'
            when f.overall_rating >= 2 then 'Low Quality'
            else 'Very Low Quality'
        end as quality_tier
        
    from facility_info f
    left join quality_claims q on f.facility_id = q.facility_id
    left join penalties p on f.facility_id = p.facility_id
    left join survey_summary s on f.facility_id = s.facility_id
)

select * from joined