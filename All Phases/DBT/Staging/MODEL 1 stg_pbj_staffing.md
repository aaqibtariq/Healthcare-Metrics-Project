

```
{{
    config(
        materialized='view',
        schema='staging'
    )
}}

with source as (
    select * from {{ source('raw', 'pbj_staffing') }}
),

renamed as (
    select
        -- IDs
        provnum as facility_id,
        provname as facility_name,
        state,
        city,
        county_name,
        
        -- Date
        workdate as work_date,
        cy_qtr as calendar_quarter,
        
        -- Census
        mdscensus as daily_census,
        
        -- RN Hours (Total = Employee + Contractor)
        hrs_rndon as rn_don_hours,
        hrs_rndon_emp as rn_don_employee_hours,
        hrs_rndon_ctr as rn_don_contractor_hours,
        
        hrs_rnadmin as rn_admin_hours,
        hrs_rnadmin_emp as rn_admin_employee_hours,
        hrs_rnadmin_ctr as rn_admin_contractor_hours,
        
        hrs_rn as rn_direct_hours,
        hrs_rn_emp as rn_direct_employee_hours,
        hrs_rn_ctr as rn_direct_contractor_hours,
        
        -- Total RN hours
        coalesce(hrs_rndon, 0) + coalesce(hrs_rnadmin, 0) + coalesce(hrs_rn, 0) 
            as total_rn_hours,
        coalesce(hrs_rndon_emp, 0) + coalesce(hrs_rnadmin_emp, 0) + coalesce(hrs_rn_emp, 0) 
            as total_rn_employee_hours,
        coalesce(hrs_rndon_ctr, 0) + coalesce(hrs_rnadmin_ctr, 0) + coalesce(hrs_rn_ctr, 0) 
            as total_rn_contractor_hours,
        
        -- LPN Hours
        hrs_lpnadmin as lpn_admin_hours,
        hrs_lpnadmin_emp as lpn_admin_employee_hours,
        hrs_lpnadmin_ctr as lpn_admin_contractor_hours,
        
        hrs_lpn as lpn_direct_hours,
        hrs_lpn_emp as lpn_direct_employee_hours,
        hrs_lpn_ctr as lpn_direct_contractor_hours,
        
        -- Total LPN hours
        coalesce(hrs_lpnadmin, 0) + coalesce(hrs_lpn, 0) as total_lpn_hours,
        coalesce(hrs_lpnadmin_emp, 0) + coalesce(hrs_lpn_emp, 0) as total_lpn_employee_hours,
        coalesce(hrs_lpnadmin_ctr, 0) + coalesce(hrs_lpn_ctr, 0) as total_lpn_contractor_hours,
        
        -- CNA Hours
        hrs_cna as cna_hours,
        hrs_cna_emp as cna_employee_hours,
        hrs_cna_ctr as cna_contractor_hours,
        
        -- Nurse Aide in Training
        hrs_natrn as na_training_hours,
        hrs_natrn_emp as na_training_employee_hours,
        hrs_natrn_ctr as na_training_contractor_hours,
        
        -- Medication Aide
        hrs_medaide as med_aide_hours,
        hrs_medaide_emp as med_aide_employee_hours,
        hrs_medaide_ctr as med_aide_contractor_hours,
        
        -- Total Nursing Hours
        coalesce(hrs_rndon, 0) + coalesce(hrs_rnadmin, 0) + coalesce(hrs_rn, 0) +
        coalesce(hrs_lpnadmin, 0) + coalesce(hrs_lpn, 0) +
        coalesce(hrs_cna, 0) as total_nursing_hours,
        
        -- Total Employee vs Contractor
        coalesce(hrs_rndon_emp, 0) + coalesce(hrs_rnadmin_emp, 0) + coalesce(hrs_rn_emp, 0) +
        coalesce(hrs_lpnadmin_emp, 0) + coalesce(hrs_lpn_emp, 0) +
        coalesce(hrs_cna_emp, 0) as total_employee_hours,
        
        coalesce(hrs_rndon_ctr, 0) + coalesce(hrs_rnadmin_ctr, 0) + coalesce(hrs_rn_ctr, 0) +
        coalesce(hrs_lpnadmin_ctr, 0) + coalesce(hrs_lpn_ctr, 0) +
        coalesce(hrs_cna_ctr, 0) as total_contractor_hours,
        
        -- Metadata
        _load_time,
        _source_file
        
    from source
    where daily_census > 0  -- Filter out records with no residents
)

select * from renamed
```
