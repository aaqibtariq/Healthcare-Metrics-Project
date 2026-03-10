{{
    config(
        materialized='table',
        schema='core'
    )
}}

-- METRIC 1: Nurse-to-Patient Staffing Ratios

with daily_staffing as (
    select * from {{ ref('int_facility_daily_staffing') }}
),

state_benchmarks as (
    select * from {{ ref('stg_state_averages') }}
),

monthly_aggregates as (
    select
        facility_id,
        facility_name,
        state,
        ownership_type,
        date_trunc('month', work_date) as month,
        
        -- Average daily metrics
        avg(daily_census) as avg_daily_census,
        avg(occupancy_rate_pct) as avg_occupancy_pct,
        
        -- Average HPRD
        avg(rn_hprd) as avg_rn_hprd,
        avg(lpn_hprd) as avg_lpn_hprd,
        avg(cna_hprd) as avg_cna_hprd,
        avg(total_nursing_hprd) as avg_total_nursing_hprd,
        
        -- Total hours
        sum(total_nursing_hours) as total_nursing_hours,
        count(*) as days_reported
        
    from daily_staffing
    group by facility_id, facility_name, state, ownership_type, month
),

with_benchmarks as (
    select
        m.*,
        b.avg_total_nursing_hprd as state_benchmark_hprd,
        b.avg_rn_hprd as state_benchmark_rn_hprd,
        
        -- Compare to benchmark
        m.avg_total_nursing_hprd - b.avg_total_nursing_hprd as variance_from_state_avg,
        
        case 
            when m.avg_total_nursing_hprd >= b.avg_total_nursing_hprd then 'At or Above Benchmark'
            when m.avg_total_nursing_hprd >= b.avg_total_nursing_hprd * 0.9 then 'Slightly Below Benchmark'
            else 'Significantly Below Benchmark'
        end as benchmark_category
        
    from monthly_aggregates m
    left join state_benchmarks b on m.state = b.state
)

select * from with_benchmarks
order by month desc, facility_id