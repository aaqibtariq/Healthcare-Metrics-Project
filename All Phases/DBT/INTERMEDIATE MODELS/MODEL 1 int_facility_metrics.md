```sql

-- models/intermediate/int_facility_metrics.sql

{{
    config(
        materialized='view',
        tags=['intermediate']
    )
}}

with staffing as (
    select * from {{ ref('stg_pbj_staffing') }}
),

facilities as (
    select * from {{ ref('stg_provider_info') }}
),

quality as (
    select
        facility_id,
        max(case when measure_code = '521' then adjusted_score end) as readmission_rate_shortstay,
        max(case when measure_code = '551' then adjusted_score end) as hospitalization_rate_longstay,
        max(case when measure_code = '522' then adjusted_score end) as ed_visit_rate_shortstay
    from {{ ref('stg_quality_claims') }}
    group by facility_id
),

joined as (
    select
        -- Dimensions
        f.facility_id,
        f.facility_name,
        f.state,
        f.city,
        f.ownership_type,
        f.certified_beds,
        f.overall_star_rating,
        
        -- Staffing aggregates (monthly)
        date_trunc('month', s.work_date) as month,
        avg(s.resident_census) as avg_monthly_census,
        avg(s.total_rn_hours / nullif(s.resident_census, 0)) as avg_rn_hprd,
        avg(s.total_lpn_hours / nullif(s.resident_census, 0)) as avg_lpn_hprd,
        avg(s.total_cna_hours / nullif(s.resident_census, 0)) as avg_cna_hprd,
        avg((s.total_rn_hours + s.total_lpn_hours + s.total_cna_hours) / nullif(s.resident_census, 0)) as avg_total_hprd,
        
        -- Workforce mix
        sum(s.total_emp_hours) as total_emp_hours,
        sum(s.total_ctr_hours) as total_ctr_hours,
        sum(s.total_emp_hours) / nullif(sum(s.total_emp_hours + s.total_ctr_hours), 0) * 100 as emp_pct,
        
        -- Quality
        q.readmission_rate_shortstay,
        q.hospitalization_rate_longstay,
        q.ed_visit_rate_shortstay
        
    from staffing s
    inner join facilities f on s.facility_id = f.facility_id
    left join quality q on f.facility_id = q.facility_id
    
    where s.resident_census > 0  -- Filter zero-census days
    
    group by
        f.facility_id,
        f.facility_name,
        f.state,
        f.city,
        f.ownership_type,
        f.certified_beds,
        f.overall_star_rating,
        date_trunc('month', s.work_date),
        q.readmission_rate_shortstay,
        q.hospitalization_rate_longstay,
        q.ed_visit_rate_shortstay
)

select * from joined

```
