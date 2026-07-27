{{ config(
    indexes=[{'columns': ['date'], 'unique': True}]
) }}

SELECT
    d::date                                  AS date,
    EXTRACT(YEAR    FROM d)::int             AS year,
    EXTRACT(MONTH   FROM d)::int             AS month,
    EXTRACT(DAY     FROM d)::int             AS day,
    EXTRACT(ISODOW  FROM d)::int             AS day_of_week,
    TO_CHAR(d, 'YYYY-MM')                    AS year_month,
    DATE_TRUNC('week',  d)::date             AS week_start,
    DATE_TRUNC('month', d)::date             AS month_start,
    EXTRACT(ISODOW FROM d) IN (6, 7)         AS is_weekend
FROM generate_series('2025-01-01'::date, '2027-12-31'::date, '1 day') as d