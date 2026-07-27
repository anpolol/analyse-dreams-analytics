SELECT
    id,
    event_name,
    occurred_at,
    anon_id,
    user_id,
    session_id,
    CASE LOWER(NULLIF(TRIM(utm_source), ''))
        WHEN 'ya' THEN 'yandex'
        ELSE LOWER(NULLIF(TRIM(utm_source), ''))
    END AS utm_source,
    LOWER(NULLIF(TRIM(utm_medium), '')) AS utm_medium,
    LOWER(NULLIF(TRIM(utm_campaign), '')) AS utm_campaign,
    platform,
    client_id,
    properties
FROM {{ source('raw_public', 'events') }}