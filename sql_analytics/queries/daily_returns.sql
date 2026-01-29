WITH prev_prices AS (
    SELECT 
        ticker,
        date,
        close,
        LAG(close) OVER (PARTITION BY ticker ORDER BY date) as prev_close
    FROM prices
)
SELECT
    ticker,
    date,
    close,
    prev_close,
    (close - prev_close) / prev_close as daily_return
FROM prev_prices;