{% set dt = modules.datetime.datetime.now() %}
{% set dt_local = modules.pytz.timezone('Australia/Sydney').localize(dt).strftime("%Y-%m-%d") %}

SELECT DISTINCT
  CAST(date as DATE) AS date,
  bgg_id,
  mechanic_id,
  mechanic
  -- (CASE WHEN mechanic_id = '<NA>' THEN NULL
  --       WHEN mechanic = '(Unknown)' THEN NULL
  --       ELSE mechanic_id
  --       END) as mechanic_id,
  -- (CASE WHEN mechanic = '<NA>' THEN NULL
  --       WHEN mechanic = '(Unknown)' THEN NULL
  --       ELSE mechanic
  --       END) as mechanic,
FROM `{{ env_var('GCP_PROJECT_ID') }}.bgg_stage.bgg-{{ dt_local }}`,
  UNNEST(SPLIT(boardgame_mechanic_id,'|,|')) AS mechanic_id WITH OFFSET b,
  UNNEST(SPLIT(boardgame_mechanic,'|,|')) AS mechanic WITH OFFSET c
WHERE b = c