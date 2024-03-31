{% set dt = modules.datetime.datetime.now() %}
{% set dt_local = modules.pytz.timezone('Australia/Sydney').localize(dt).strftime("%Y-%m-%d") %}

SELECT DISTINCT
  CAST(date as DATE) AS date,
  bgg_id,
  designer_id,
  designer
  -- (CASE WHEN designer_id = '<NA>' THEN NULL
  --       WHEN designer = '(Unknown)' THEN NULL
  --       ELSE designer_id
  --       END) as designer_id,
  -- (CASE WHEN designer = '<NA>' THEN NULL
  --       WHEN designer = '(Unknown)' THEN NULL
  --       ELSE designer
  --       END) as designer,
FROM `{{ env_var('GCP_PROJECT_ID') }}.bgg_stage.bgg-{{ dt_local }}`,
  UNNEST(SPLIT(boardgame_designer_id,'|,|')) AS designer_id WITH OFFSET b,
  UNNEST(SPLIT(boardgame_designer,'|,|')) AS designer WITH OFFSET c
WHERE b = c