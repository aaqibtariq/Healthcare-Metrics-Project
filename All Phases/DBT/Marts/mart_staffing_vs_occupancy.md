```sql

{{
    config(
        materialized='table',
        schema='core'
    )
}}

-- METRIC 2: Staffing vs Occupancy Correlation

with daily_staffing as (
    select * from {{ ref('int_facility_daily_staffing') }}
),

facility_correlations as (
    select
        facility_id,
        facility_name,
        state,
        
        -- Occupancy statistics
        avg(occupancy_rate_pct) as avg_occupancy_pct,
        min(occupancy_rate_pct) as min_occupancy_pct,
        max(occupancy_rate_pct) as max_occupancy_pct,
        stddev(occupancy_rate_pct) as occupancy_volatility,
        
        -- Staffing statistics
        avg(total_nursing_hprd) as avg_nursing_hprd,
        stddev(total_nursing_hprd) as nursing_hprd_volatility,
        
        -- Correlation approximation
        corr(occupancy_rate_pct, total_nursing_hprd) as staffing_occupancy_correlation,
        
        -- Count days by occupancy level
        count(case when occupancy_rate_pct < 70 then 1 end) as days_low_occupancy,
        count(case when occupancy_rate_pct between 70 and 85 then 1 end) as days_medium_occupancy,
        count(case when occupancy_rate_pct > 85 then 1 end) as days_high_occupancy,
        
        -- Staffing efficiency
        avg(case when occupancy_rate_pct > 85 then total_nursing_hprd end) as avg_hprd_high_occupancy,
        avg(case when occupancy_rate_pct < 70 then total_nursing_hprd end) as avg_hprd_low_occupancy,
        
        count(*) as total_days
        
    from daily_staffing
    group by facility_id, facility_name, state
),

with_insights as (
    select
        *,
        
        -- Staffing flexibility score
        case 
            when avg_hprd_high_occupancy - avg_hprd_low_occupancy > 0.5 
            then 'High Flexibility'
            when avg_hprd_high_occupancy - avg_hprd_low_occupancy > 0.2 
            then 'Medium Flexibility'
            else 'Low Flexibility'
        end as staffing_flexibility,
        
        -- Occupancy utilization
        case 
            when avg_occupancy_pct >= 85 then 'High Utilization'
            when avg_occupancy_pct >= 70 then 'Medium Utilization'
            else 'Low Utilization'
        end as occupancy_utilization_category
        
    from facility_correlations
)

select * from with_insights
order by facility_id


```
