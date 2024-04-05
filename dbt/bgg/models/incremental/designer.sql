{{
    config(
        materialized='incremental',
        unique_key=['date','bgg_id','designer_id'],
        incremental_strategy="merge",
        on_schema_change='fail'
    )
}}

SELECT
    *
FROM {{ ref('fact_designer') }}