{% set dt = modules.datetime.datetime.now(modules.pytz.timezone('UTC')) %}
{% set dt_local = dt.astimezone(modules.pytz.timezone('Australia/Sydney')).strftime("%Y-%m-%d") %}

SELECT DISTINCT
  CAST(date AS DATE) AS date,
  bgg_id,
  CAST(designer_id AS INT) AS designer_id,
  designer,
FROM `{{ env_var('GCP_PROJECT_ID') }}.bgg_stage.bgg-{{ dt_local }}`,
  UNNEST(SPLIT(boardgame_designer_id,'|,|')) AS designer_id WITH OFFSET b,
  UNNEST(SPLIT(boardgame_designer,'|,|')) AS designer WITH OFFSET c
WHERE b = c
AND designer NOT IN ('(Public Domain)','(Reader Contribution)','<NA>','(Uncredited)')
AND designer_id NOT IN ('<NA>')