SELECT
    d.date,
    COALESCE(e.visits,          0) AS visits,
    COALESCE(e.visitors,        0) AS visitors,
    COALESCE(e.registrations,   0) AS registrations,
    COALESCE(e.activated,       0) AS activated,
    COALESCE(p.paying,          0) AS paying,
    COALESCE(p.payments_count,  0) AS payments_count,
    COALESCE(p.revenue,         0) AS revenue
FROM {{ ref('dim_date') }} d
LEFT JOIN (
    SELECT
        DATE(occurred_at) AS date,
        COUNT(*)                   FILTER (WHERE event_name = 'session_started')         AS visits,
        COUNT(DISTINCT anon_id)    FILTER (WHERE event_name = 'session_started')         AS visitors,
        COUNT(DISTINCT user_id)    FILTER (WHERE event_name = 'registration_completed')  AS registrations,
        COUNT(DISTINCT user_id)    FILTER (WHERE event_name = 'dream_submitted')         AS activated
    FROM {{ ref('stg_events' )}}
    GROUP BY DATE(occurred_at)
) e ON e.date = d.date
LEFT JOIN (
    SELECT
        DATE(payment_date) AS date,
        COUNT(DISTINCT user_id) FILTER (WHERE is_successful) AS paying,
        COUNT(*)                FILTER (WHERE is_successful) AS payments_count,
        SUM(amount)             FILTER (WHERE is_successful) AS revenue
    FROM {{ ref('stg_payments') }}
    GROUP BY DATE(payment_date)
) p ON p.date = d.date
WHERE d.date >= (SELECT MIN(DATE(occurred_at)) FROM {{ ref('stg_events') }})
  AND d.date <= CURRENT_DATE
ORDER BY d.date