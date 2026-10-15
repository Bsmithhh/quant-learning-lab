-- Find days where the open differed from the previous close by more than 2%
-- The CTE computes prev_close; the outer query uses it. An alias can't be
-- referenced in the same SELECT list that defines it.
WITH prev_prices as(
    SELECT
    ticker,
    date,
    open,
    LAG(close) OVER (PARTITION BY ticker ORDER BY date) as prev_close
    FROM prices
)

SELECT
ticker,
date,
prev_close,
open,
(open - prev_close) / prev_close as gap
FROM prev_prices
WHERE ABS((open - prev_close) / prev_close) > 0.02
ORDER BY ABS(gap) DESC
