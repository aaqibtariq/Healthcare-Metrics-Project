

# DBT Notes


##  DBT Pipeline Diagram
<p align="center">
  <img src="https://raw.githubusercontent.com/aaqibtariq/Healthcare-Metrics-Project/blob/main/All%20Phases/DBT/image%20-%202026-03-18T134333.439.jpg" width="800"/>
</p>


LEFT SIDE - SOURCES (Green/Blue):

- raw.state_averages (SRC - green source table)
- stg_quality_claims (MDL - blue staging model)
- stg_penalties
- stg_provider_info
- stg_survey_summary
- stg_pbj_staffing

MIDDLE - INTERMEDIATE LAYER:

- int_facility_quality_scores ← Joins multiple staging tables
- int_facility_daily_staffing ← Combines staffing + provider data
- int_facility_risk_factors ← Risk assessment calculations

RIGHT SIDE - BUSINESS METRICS (Your 5 Marts!):

- mart_high_risk_facilities  - Critical facilities needing intervention
- mart_staffing_ratios  - Monthly staffing benchmarks
- mart_staffing_vs_quality  - Staffing impact on quality
- mart_employee_vs_contractor  - Workforce composition
- mart_staffing_vs_occupancy  - Occupancy vs staffing correlation


 WHAT THIS SHOWS:
- Clean Architecture - Source → Staging → Intermediate → Marts
- Proper Layering - Each layer builds on the previous
- Clear Dependencies - You can see exactly how data flows
- Reusable Components - Intermediate models feed multiple marts


Whats done

- 16 dbt models transforming 1.6M+ rows
- 50 data quality tests (100% passing!)
- Interactive documentation with visual lineage
- 5 business-critical metrics ready for dashboards
- Clean, maintainable architecture

  
