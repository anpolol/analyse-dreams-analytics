SELECT
    date,
    LOWER(NULLIF(TRIM(utm_source), '')) AS utm_source,
    SUM(cost)   AS cost,
    SUM(clicks) AS clicks
FROM {{ source('raw', 'ad_costs') }}
GROUP BY date, LOWER(NULLIF(TRIM(utm_source), ''))