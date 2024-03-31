{% set dt = modules.datetime.datetime.now() %}
{% set dt_local = modules.pytz.timezone('Australia/Sydney').localize(dt).strftime("%Y-%m-%d") %}

SELECT DISTINCT
  CAST(date as DATE) AS date,
  bgg_id,
  (CASE WHEN publisher_id = '<NA>' THEN NULL
        WHEN publisher = '(Unknown)' THEN NULL
        ELSE publisher_id
        END) as publisher_id,
  (CASE WHEN publisher = '<NA>' THEN NULL
        WHEN publisher = '(Unknown)' THEN NULL
        ELSE publisher
        END) as publisher,
FROM `{{ env_var('GCP_PROJECT_ID') }}.bgg_stage.bgg-{{ dt_local }}`,
  UNNEST(SPLIT(boardgame_publisher_id,'|,|')) AS publisher_id WITH OFFSET b,
  UNNEST(SPLIT(boardgame_publisher,'|,|')) AS publisher WITH OFFSET c
WHERE b = c