SELECT 
  date,
  bgg_id,
  suggested_player_count,
  player_count_recommendation,
FROM {{ ref('fact_suggested_players_full')}}
WHERE 1=1
AND player_count_recommendation IS NOT NULL