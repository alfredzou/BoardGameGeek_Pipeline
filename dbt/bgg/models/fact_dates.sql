SELECT
    date,
    EXTRACT(YEAR FROM date) AS year,
    EXTRACT(MONTH FROM date) AS month,
    EXTRACT(DAY FROM date) AS day,
    EXTRACT(DAYOFWEEK FROM date) AS day_of_week,
    EXTRACT(DAYOFYEAR FROM date) AS day_of_year,
    EXTRACT(WEEK(MONDAY) FROM date) AS week_of_year,
    EXTRACT(QUARTER FROM date) AS quarter,
    DATE_DIFF(date, '2024-01-01', DAY) + 1 AS day_id
FROM UNNEST(GENERATE_DATE_ARRAY('2024-01-01', '2025-12-31')) AS date