WITH prev_prices as(
    SELECT
    ticker,
    date,
    close,
    open,
    LAG(close) OVER (PARTITION BY ticker ORDER BY date) as prev_close,
    (open - prev_close) / prev_close  as gap
    FROM prices
)

SELECT
ticker,
date,
prev_close,
open,
gap
FROM prev_prices WHERE ABS(gap) > 0.02 ORDER BY ABS(gap) DESC

