{% set dt = modules.datetime.datetime.now() %}
{% set dt_local = modules.pytz.timezone('Australia/Sydney').localize(dt).strftime("%Y-%m-%d") %}

SELECT DISTINCT
  CAST(date as DATE) AS date,
  bgg_id,
  CAST(artist_id AS INT) AS artist_id,
  artist,
FROM `{{ env_var('GCP_PROJECT_ID') }}.bgg_stage.bgg-{{ dt_local }}`,
  UNNEST(SPLIT(boardgame_artist_id,'|,|')) AS artist_id WITH OFFSET b,
  UNNEST(SPLIT(boardgame_artist,'|,|')) AS artist WITH OFFSET c
WHERE b = c
AND artist NOT IN ('<NA>','(Uncredited)') AND artist_id NOT IN ('<NA>')