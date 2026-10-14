WITH sources AS (
    SELECT DISTINCT utm_source FROM {{ ref('visits_by_source') }}
),
spine AS (
    SELECT d.date, s.utm_source
    FROM {{ ref('dim_date') }} d
    CROSS JOIN sources s
    WHERE d.date >= (SELECT MIN(date) FROM {{ ref('visits_by_source') }})
      AND d.date <= CURRENT_DATE
)
SELECT
    sp.date,
    sp.utm_source,
    COALESCE(v.visits,        0) AS visits,
    COALESCE(v.visitors,      0) AS visitors,
    COALESCE(r.registrations, 0) AS registrations,
    COALESCE(a.activated,     0) AS activated,
    COALESCE(p.paying,        0) AS paying,
    COALESCE(p.revenue,       0) AS revenue,
    COALESCE(c.cost,          0) AS cost
FROM spine sp
LEFT JOIN {{ ref('visits_by_source') }}        v ON v.date = sp.date AND v.utm_source = sp.utm_source
LEFT JOIN {{ ref('registrations_by_source') }} r ON r.date = sp.date AND r.utm_source = sp.utm_source
LEFT JOIN {{ ref('activated_by_source') }}     a ON a.date = sp.date AND a.utm_source = sp.utm_source
LEFT JOIN {{ ref('revenue_by_source') }}       p ON p.date = sp.date AND p.utm_source = sp.utm_source
LEFT JOIN {{ ref('stg_ad_costs') }}            c ON c.date = sp.date AND c.utm_source = sp.utm_source
ORDER BY sp.date, sp.utm_source