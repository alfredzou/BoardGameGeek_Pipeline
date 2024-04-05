{{
    config(
        materialized='incremental',
        unique_key=['date','bgg_id','suggested_player_count','player_count_rating'],
        incremental_strategy="merge",
        on_schema_change='fail'
    )
}}

SELECT
    *
FROM {{ ref('fact_suggested_players_full') }}