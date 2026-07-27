    SELECT
        DATE(activated_at) AS date,
        COALESCE(utm_source, 'direct') AS utm_source,
        COUNT(*) AS activated
    FROM {{ ref('dim_users') }}
    WHERE activated_at IS NOT NULL
    GROUP BY DATE(activated_at), COALESCE(utm_source, 'direct')
