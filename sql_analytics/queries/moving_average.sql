-- Calculate 20-day simple moving average of closing prices
-- Uses window function to preserve all rows while computing rolling average
-- Partitioned by ticker to handle multiple assets

SELECT
    ticker,
    close,
    date,
    AVG(close) OVER(
        PARTITION BY ticker
        ORDER BY date
        ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
    ) as ma_20
FROM prices
    