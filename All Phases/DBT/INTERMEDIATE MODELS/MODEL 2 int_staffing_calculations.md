```sql

{{
    config(
        materialized='view',
        schema='intermediate'
    )
}}

with daily_staffing as (
    select * from {{ ref('stg_pbj_staffing') }}
),

facility_info as (
    select * from {{ ref('stg_provider_info') }}
),

joined as (
    select
        -- Facility details
        f.facility_id,
        f.facility_name,
        f.state,
        f.ownership_type,
        f.certified_beds,
        f.overall_rating,
        
        -- Daily staffing
        s.work_date,
        s.calendar_quarter,
        s.daily_census,
        
        -- Hours
        s.total_rn_hours,
        s.total_lpn_hours,
        s.cna_hours,
        s.total_nursing_hours,
        
        -- Employee vs Contractor
        s.total_employee_hours,
        s.total_contractor_hours,
        
        -- Calculate hours per resident per day (HPRD)
        case 
            when s.daily_census > 0 
            then s.total_rn_hours / s.daily_census 
            else null 
        end as rn_hprd,
        
        case 
            when s.daily_census > 0 
            then s.total_lpn_hours / s.daily_census 
            else null 
        end as lpn_hprd,
        
        case 
            when s.daily_census > 0 
            then s.cna_hours / s.daily_census 
            else null 
        end as cna_hprd,
        
        case 
            when s.daily_census > 0 
            then s.total_nursing_hours / s.daily_census 
            else null 
        end as total_nursing_hprd,
        
        -- Occupancy rate
        case 
            when f.certified_beds > 0 
            then (s.daily_census::float / f.certified_beds) * 100 
            else null 
        end as occupancy_rate_pct,
        
        -- Contractor percentage
        case 
            when s.total_nursing_hours > 0 
            then (s.total_contractor_hours::float / s.total_nursing_hours) * 100 
            else null 
        end as contractor_pct
        
    from daily_staffing s
    inner join facility_info f on s.facility_id = f.facility_id
)

select * from joined


```
