```sql

{{
    config(
        materialized='table',
        schema='core'
    )
}}

-- METRIC 4: Employee vs Contractor Staffing Mix

with daily_staffing as (
    select * from {{ ref('int_facility_daily_staffing') }}
),

monthly_mix as (
    select
        facility_id,
        facility_name,
        state,
        ownership_type,
        date_trunc('month', work_date) as month,
        
        -- Total hours
        sum(total_employee_hours) as total_employee_hours,
        sum(total_contractor_hours) as total_contractor_hours,
        sum(total_nursing_hours) as total_nursing_hours,
        
        -- Percentages
        case 
            when sum(total_nursing_hours) > 0 
            then (sum(total_employee_hours)::float / sum(total_nursing_hours)) * 100 
            else 0 
        end as employee_pct,
        
        case 
            when sum(total_nursing_hours) > 0 
            then (sum(total_contractor_hours)::float / sum(total_nursing_hours)) * 100 
            else 0 
        end as contractor_pct,
        
        count(*) as days_reported
        
    from daily_staffing
    group by facility_id, facility_name, state, ownership_type, month
),

with_insights as (
    select
        *,
        
        -- Staffing model categorization
        case 
            when contractor_pct >= 50 then 'Contractor Dependent'
            when contractor_pct >= 25 then 'Mixed Model'
            when contractor_pct >= 10 then 'Primarily Employee'
            else 'Employee Only'
        end as staffing_model,
        
        -- Cost implications (approximate)
        -- Contractors typically cost 1.5x to 2x employee rates
        total_employee_hours + (total_contractor_hours * 1.75) as estimated_cost_equivalent_hours
        
    from monthly_mix
)

select * from with_insights
order by month desc, contractor_pct desc


```
