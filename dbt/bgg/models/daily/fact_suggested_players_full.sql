{% set dt = modules.datetime.datetime.now(modules.pytz.timezone('UTC')) %}
{% set dt_local = dt.astimezone(modules.pytz.timezone('Australia/Sydney')).strftime("%Y-%m-%d") %}

WITH my_cte AS (
SELECT DISTINCT
  CAST(date AS DATE) AS date,
  bgg_id,
  suggested_player_count,
  player_count_rating,
  CAST(player_count_votes AS INT) AS player_count_votes,
FROM `{{ env_var('GCP_PROJECT_ID') }}.bgg_stage.sp-{{ dt_local }}`,
  UNNEST(SPLIT(player_count_rating,'|,|')) AS player_count_rating WITH OFFSET b,
  UNNEST(SPLIT(player_count_votes,'|,|')) AS player_count_votes WITH OFFSET c
WHERE b = c
AND player_count_rating <> "<NA>" AND player_count_votes <> "<NA>"
), my_cte2 AS (
SELECT
  date,
  bgg_id,
  suggested_player_count,
  player_count_rating,
  player_count_votes,
  SUM(player_count_votes) OVER(PARTITION BY bgg_id, suggested_player_count) AS total_votes_by_player_count,
  SUM(player_count_votes) OVER(PARTITION BY bgg_id) as total_votes,
  CAST((CASE WHEN player_count_votes = 0 THEN NULL ELSE 100*player_count_votes/SUM(player_count_votes) OVER(PARTITION BY bgg_id, suggested_player_count) END) AS int) AS perc_by_player_count,
  CAST((CASE WHEN player_count_votes = 0 THEN NULL ELSE 100*player_count_votes/SUM(player_count_votes) OVER(PARTITION BY bgg_id) END) AS int) AS perc_total_votes,
  RANK() OVER(PARTITION BY bgg_id, suggested_player_count ORDER BY player_count_votes DESC) AS rank_by_player_count,
FROM my_cte
)

SELECT
  date,
  bgg_id,
  suggested_player_count,
  player_count_rating,
  player_count_votes,
  total_votes_by_player_count,
  total_votes,
  perc_by_player_count,
  perc_total_votes,
  rank_by_player_count,
  (CASE WHEN RIGHT(suggested_player_count,1) = "+" THEN NULL
        WHEN total_votes_by_player_count <5 THEN NULL
        WHEN rank_by_player_count = 1 THEN player_count_rating
  END) AS player_count_recommendation
FROM my_cte2