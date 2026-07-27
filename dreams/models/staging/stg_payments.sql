SELECT
    id,
    user_id,
    payment_date,
    amount,
    payment_id,
    status,
    dreams_count,
    payment_type,
    (status = 'succeeded') AS is_successful
FROM {{ source('raw_public', 'users_payment') }}