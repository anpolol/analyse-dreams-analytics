SELECT
    e.user_id,
    t.utm_source,
    t.utm_medium,
    t.utm_campaign,
    t.first_touch_at,
    e.registered_at,
    e.activated_at,
    p.first_payment_at,
    COALESCE(p.total_revenue, 0) AS total_revenue
FROM (
    SELECT
        user_id,
        MIN(occurred_at) FILTER (WHERE event_name = 'registration_completed') AS registered_at,
        MIN(occurred_at) FILTER (WHERE event_name = 'dream_submitted')        AS activated_at
    FROM {{ ref('stg_events') }}
    WHERE user_id IS NOT NULL
    GROUP BY user_id
) e
LEFT JOIN (
    SELECT DISTINCT ON (user_id)
        user_id,
        utm_source,
        utm_medium,
        utm_campaign,
        occurred_at AS first_touch_at
    FROM {{ ref('stg_events') }}
    WHERE utm_source IS NOT NULL
      AND user_id IS NOT NULL
    ORDER BY user_id, occurred_at
) t ON t.user_id = e.user_id
LEFT JOIN (
    SELECT
        user_id,
        MIN(payment_date) FILTER (WHERE is_successful) AS first_payment_at,
        SUM(amount)       FILTER (WHERE is_successful) AS total_revenue
    FROM {{ ref('stg_payments') }}
    GROUP BY user_id
) p ON p.user_id = e.user_id