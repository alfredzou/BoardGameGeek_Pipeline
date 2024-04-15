{% set dt = modules.datetime.datetime.now(modules.pytz.timezone('UTC')) %}
{% set dt_local = dt.astimezone(modules.pytz.timezone('Australia/Sydney')).strftime("%Y-%m-%d") %}

SELECT DISTINCT
  CAST(date as DATE) AS date,
  bgg_id,
  CAST(publisher_id AS INT) AS publisher_id,
  publisher,
FROM `{{ env_var('GCP_PROJECT_ID') }}.bgg_stage.bgg-{{ dt_local }}`,
  UNNEST(SPLIT(boardgame_publisher_id,'|,|')) AS publisher_id WITH OFFSET b,
  UNNEST(SPLIT(boardgame_publisher,'|,|')) AS publisher WITH OFFSET c
WHERE b = c
AND publisher NOT IN ('<NA>','(Uncredited)') AND publisher_id NOT IN ('<NA>')