{% set dt = modules.datetime.datetime.now(modules.pytz.timezone('UTC')) %}
{% set dt_local = dt.astimezone(modules.pytz.timezone('Australia/Sydney')).strftime("%Y-%m-%d") %}

SELECT DISTINCT
  CAST(date AS DATE) AS date,
  bgg_id,
  CAST(category_id AS INT) AS category_id,
  category,
FROM `{{ env_var('GCP_PROJECT_ID') }}.bgg_stage.bgg-{{ dt_local }}`,
  UNNEST(SPLIT(boardgame_category_id,'|,|')) AS category_id WITH OFFSET b,
  UNNEST(SPLIT(boardgame_category,'|,|')) AS category WITH OFFSET c
WHERE b = c
AND category NOT IN ('<NA>') AND category_id NOT IN ('<NA>')