{% set dt = modules.datetime.datetime.now() %}
{% set dt_local = modules.pytz.timezone('Australia/Sydney').localize(dt).strftime("%Y-%m-%d") %}

SELECT DISTINCT
  CAST(date as DATE) AS date,
  bgg_id,
  category_id,
  category
  -- (CASE WHEN category_id = '<NA>' THEN NULL
  --       WHEN category = '(Unknown)' THEN NULL
  --       ELSE category_id
  --       END) as category_id,
  -- (CASE WHEN category = '<NA>' THEN NULL
  --       WHEN category = '(Unknown)' THEN NULL
  --       ELSE category
  --       END) as category,
FROM `{{ env_var('GCP_PROJECT_ID') }}.bgg_stage.bgg-{{ dt_local }}`,
  UNNEST(SPLIT(boardgame_category_id,'|,|')) AS category_id WITH OFFSET b,
  UNNEST(SPLIT(boardgame_category,'|,|')) AS category WITH OFFSET c
WHERE b = c