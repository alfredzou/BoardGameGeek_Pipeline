{% set dt = modules.datetime.datetime.now() %}
{% set dt_local = modules.pytz.timezone('Australia/Sydney').localize(dt).strftime("%Y-%m-%d") %}

SELECT DISTINCT
  CAST(date as DATE) AS date,
  bgg_id,
  family_id,
  family
  -- (CASE WHEN family_id = '<NA>' THEN NULL
  --       WHEN family = '(Unknown)' THEN NULL
  --       ELSE family_id
  --       END) as family_id,
  -- (CASE WHEN family = '<NA>' THEN NULL
  --       WHEN family = '(Unknown)' THEN NULL
  --       ELSE family
  --       END) as family,
FROM `{{ env_var('GCP_PROJECT_ID') }}.bgg_stage.bgg-{{ dt_local }}`,
  UNNEST(SPLIT(boardgame_family_id,'|,|')) AS family_id WITH OFFSET b,
  UNNEST(SPLIT(boardgame_family,'|,|')) AS family WITH OFFSET c
WHERE b = c