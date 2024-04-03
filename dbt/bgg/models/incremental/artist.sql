{{
    config(
        materialized='incremental',
        unique_key=['date','bgg_id','artist_id'],
        on_schema_change='fail'
    )
}}

SELECT
    *
FROM {{ ref('fact_artist') }}