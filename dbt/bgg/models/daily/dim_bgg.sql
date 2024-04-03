{% set dt = modules.datetime.datetime.now() %}
{% set dt_local = modules.pytz.timezone('Australia/Sydney').localize(dt).strftime("%Y-%m-%d") %}

SELECT 
  CAST(date AS DATE) AS date,
  bgg_id,
  CASE WHEN type = 'boardgameexpansion' THEN 'expansion' ELSE type END AS type,
  name,
  url,
  (CASE WHEN year_published = 0 THEN NULL ELSE year_published END) AS year_published,
  (CASE WHEN min_players = 0 THEN NULL ELSE min_players END) AS min_players,
  (CASE WHEN max_players = 0 THEN NULL ELSE max_players END) AS max_players,
  (CASE WHEN play_time = 0 THEN NULL ELSE play_time END) AS play_time,
  (CASE WHEN min_play_time = 0 THEN NULL ELSE min_play_time END) AS min_play_time,
  (CASE WHEN max_play_time = 0 THEN NULL ELSE max_play_time END) AS max_play_time,
  num_ratings,
  (CASE WHEN avg_rating = 0 THEN NULL ELSE avg_rating END) AS avg_rating,
  (CASE WHEN standard_deviation_rating = 0 THEN NULL ELSE standard_deviation_rating END) AS standard_deviation_rating,
  (CASE WHEN bayesian_avg_rating = 0 THEN NULL ELSE bayesian_avg_rating END) AS geek_rating,
  num_comments,
  num_complexity_ratings,
  (CASE WHEN avg_complexity_rating = 0 THEN NULL ELSE avg_complexity_rating END) AS avg_complexity_rating,
  (CASE WHEN avg_complexity_rating = 0 THEN NULL
        WHEN avg_complexity_rating < 2 THEN 'Light'
        WHEN avg_complexity_rating < 3 THEN 'Medium light'
        WHEN avg_complexity_rating < 4 THEN 'Medium heavy'
        WHEN avg_complexity_rating <= 5  THEN 'Heavy'
        END) AS avg_complexity,
  num_own,
  num_wishlist,
  num_for_trade,
  num_want_in_trade,
  CAST((CASE WHEN bgg_rank = 'Not Ranked' THEN NULL ELSE bgg_rank END) AS INTEGER) AS bgg_rank
FROM `{{ env_var('GCP_PROJECT_ID') }}.bgg_stage.bgg-{{ dt_local }}`