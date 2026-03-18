```sql

-- models/intermediate/int_quality_scores.sql

{{
    config(
        materialized='view',
        tags=['intermediate', 'quality']
    )
}}

with quality_data as (
    select
        facility_id,
        facility_name,
        state,
        overall_star_rating,
        readmission_rate_shortstay,
        hospitalization_rate_longstay,
        ed_visit_rate_shortstay
    from {{ ref('int_facility_metrics') }}
),

penalties as (
    select
        facility_id,
        sum(fine_amount) as total_penalties
    from {{ ref('stg_penalties') }}
    group by facility_id
),

composite_scores as (
    select
        q.*,
        coalesce(p.total_penalties, 0) as total_penalties,
        
        -- Quality score (0-100, higher is better)
        (
            (5 - coalesce(q.overall_star_rating, 0)) * 20  -- Star rating inverted
            + (100 - coalesce(q.readmission_rate_shortstay, 0))  -- Lower readmissions better
            + case when coalesce(p.total_penalties, 0) = 0 then 20 else 0 end  -- Bonus for no penalties
        ) / 3 as composite_quality_score,
        
        -- Quality tier
        case
            when q.overall_star_rating >= 4 then 'High Quality'
            when q.overall_star_rating >= 3 then 'Medium Quality'
            when q.overall_star_rating >= 2 then 'Low Quality'
            else 'Very Low Quality'
        end as quality_tier
        
    from quality_data q
    left join penalties p on q.facility_id = p.facility_id
)

select * from composite_scores


```
