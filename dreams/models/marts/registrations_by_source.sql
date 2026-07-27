SELECT
        DATE(registered_at) AS date,
        COALESCE(utm_source, 'direct') AS utm_source,
        COUNT(*) AS registrations
    FROM {{ ref('dim_users') }}
    WHERE registered_at IS NOT NULL
    GROUP BY DATE(registered_at), COALESCE(utm_source, 'direct')