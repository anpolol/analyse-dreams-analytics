SELECT
        DATE(first_payment_at) AS date,
        COALESCE(utm_source, 'direct') AS utm_source,
        COUNT(*) AS paying,
        SUM(total_revenue) AS revenue
    FROM {{ ref('dim_users') }}
    WHERE first_payment_at IS NOT NULL
    GROUP BY DATE(first_payment_at), COALESCE(utm_source, 'direct')