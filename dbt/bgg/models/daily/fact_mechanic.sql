{% set dt = modules.datetime.datetime.now() %}
{% set dt_local = modules.pytz.timezone('Australia/Sydney').localize(dt).strftime("%Y-%m-%d") %}

SELECT DISTINCT
  CAST(date as DATE) AS date,
  bgg_id,
  CAST(mechanic_id AS INT) AS mechanic_id,
  mechanic,
FROM `{{ env_var('GCP_PROJECT_ID') }}.bgg_stage.bgg-{{ dt_local }}`,
  UNNEST(SPLIT(boardgame_mechanic_id,'|,|')) AS mechanic_id WITH OFFSET b,
  UNNEST(SPLIT(boardgame_mechanic,'|,|')) AS mechanic WITH OFFSET c
WHERE b = c
AND mechanic NOT IN ('<NA>') AND mechanic_id NOT IN ('<NA>')