{{
    config(
        materialized='incremental',
        unique_key=['date','bgg_id'],
        incremental_strategy="merge",
        on_schema_change='fail'
    )
}}

SELECT
    *
FROM {{ ref('dim_bgg') }}