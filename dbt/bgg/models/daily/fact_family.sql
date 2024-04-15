{% set dt = modules.datetime.datetime.now(modules.pytz.timezone('UTC')) %}
{% set dt_local = dt.astimezone(modules.pytz.timezone('Australia/Sydney')).strftime("%Y-%m-%d") %}

SELECT DISTINCT
  CAST(date AS DATE) AS date,
  bgg_id,
  CAST(family_id AS INT) AS family_id,
  family,
FROM `{{ env_var('GCP_PROJECT_ID') }}.bgg_stage.bgg-{{ dt_local }}`,
  UNNEST(SPLIT(boardgame_family_id,'|,|')) AS family_id WITH OFFSET b,
  UNNEST(SPLIT(boardgame_family,'|,|')) AS family WITH OFFSET c
WHERE b = c
AND family NOT IN ('<NA>') AND family_id NOT IN ('<NA>')