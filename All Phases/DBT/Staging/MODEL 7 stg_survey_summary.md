```sql

{{
    config(
        materialized='view',
        schema='staging'
    )
}}

with source as (
    select * from {{ source('raw', 'survey_summary') }}
),

renamed as (
    select
        ccn as facility_id,
        inspection_cycle,
        health_survey_date,
        fire_safety_survey_date,
        
        -- Total deficiencies
        total_number_of_health_deficiencies,
        total_number_of_fire_safety_deficiencies,
        
        -- Health deficiency categories
        count_of_freedom_from_abuse_and_neglect_and_exploitation_deficiencies as abuse_neglect_deficiencies,
        count_of_quality_of_life_and_care_deficiencies as quality_of_life_deficiencies,
        count_of_nursing_and_physician_services_deficiencies as nursing_services_deficiencies,
        count_of_infection_control_deficiencies as infection_control_deficiencies,
        
        processing_date,
        _load_time
        
    from source
)

select * from renamed


```
