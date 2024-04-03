{% test unique_id_pair(model, column_name_id, column_name) %}

    WITH mycte AS (
    SELECT DISTINCT {{ column_name_id }}, {{ column_name }}
    FROM {{ model }}
    )

    SELECT {{ column_name_id }}, COUNT(*)
    FROM mycte
    GROUP BY {{ column_name_id }}
    HAVING COUNT(*) > 1

{% endtest %}