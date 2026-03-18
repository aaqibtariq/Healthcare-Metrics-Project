```sql

-- models/intermediate/int_staffing_calculations.sql

{{
    config(
        materialized='view',
        tags=['intermediate', 'staffing']
    )
}}

with facility_staffing as (
    select * from {{ ref('int_facility_metrics') }}
),

state_benchmarks as (
    select
        state,
        avg(avg_total_hprd) as state_avg_hprd
    from {{ ref('int_facility_metrics') }}
    group by state
),

with_benchmarks as (
    select
        f.*,
        
        -- State benchmark comparison
        b.state_avg_hprd,
        f.avg_total_hprd - b.state_avg_hprd as hprd_vs_state,
        (f.avg_total_hprd / nullif(b.state_avg_hprd, 0) - 1) * 100 as pct_above_state,
        
        -- Occupancy rate
        f.avg_monthly_census / nullif(f.certified_beds, 0) * 100 as occupancy_rate,
        
        -- Staffing adequacy
        case
            when f.avg_total_hprd >= b.state_avg_hprd * 1.2 then 'High Staffing'
            when f.avg_total_hprd >= b.state_avg_hprd * 0.8 then 'Adequate Staffing'
            else 'Low Staffing'
        end as staffing_category
        
    from facility_staffing f
    left join state_benchmarks b on f.state = b.state
)

select * from with_benchmarks

```
