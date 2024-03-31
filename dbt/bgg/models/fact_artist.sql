{% set dt = modules.datetime.datetime.now() %}
{% set dt_local = modules.pytz.timezone('Australia/Sydney').localize(dt).strftime("%Y-%m-%d") %}

SELECT DISTINCT
  CAST(date as DATE) AS date,
  bgg_id,
  (CASE WHEN artist_id = '<NA>' THEN NULL
        WHEN artist = '(Uncredited)' THEN NULL
        ELSE artist_id
        END) as artist_id,
  (CASE WHEN artist = '<NA>' THEN NULL
        WHEN artist = '(Uncredited)' THEN NULL
        ELSE artist
        END) as artist,
FROM `{{ env_var('GCP_PROJECT_ID') }}.bgg_stage.bgg-{{ dt_local }}`,
  UNNEST(SPLIT(boardgame_artist_id,'|,|')) AS artist_id WITH OFFSET b,
  UNNEST(SPLIT(boardgame_artist,'|,|')) AS artist WITH OFFSET c
WHERE b = c