```sql

{{
    config(
        materialized='view',
        schema='staging'
    )
}}

with source as (
    select * from {{ source('raw', 'quality_claims') }}
),

renamed as (
    select
        ccn as facility_id,
        measure_code,
        measure_description,
        resident_type,
        
        -- Scores
        adjusted_score,
        observed_score,
        expected_score,
        
        -- Metadata
        measure_period,
        processing_date,
        _load_time
        
    from source
),

pivoted as (
    select
        facility_id,
        processing_date,
        
        -- Measure 521: Short-stay readmission rate
        max(case when measure_code = 521 then adjusted_score end) as readmission_rate_short_stay,
        
        -- Measure 522: Short-stay ED visit rate  
        max(case when measure_code = 522 then adjusted_score end) as ed_visit_rate_short_stay,
        
        -- Measure 551: Long-stay hospitalization rate
        max(case when measure_code = 551 then adjusted_score end) as hospitalization_rate_long_stay,
        
        -- Measure 552: Long-stay ED visit rate
        max(case when measure_code = 552 then adjusted_score end) as ed_visit_rate_long_stay
        
    from renamed
    group by facility_id, processing_date
)

select * from pivoted

```
