    SELECT
        DATE(occurred_at) AS date,
        COALESCE(utm_source, 'direct') AS utm_source,
        COUNT(*)                FILTER (WHERE event_name = 'session_started') AS visits,
        COUNT(DISTINCT anon_id) FILTER (WHERE event_name = 'session_started') AS visitors
    FROM {{ ref('stg_events') }}
    GROUP BY DATE(occurred_at), COALESCE(utm_source, 'direct')