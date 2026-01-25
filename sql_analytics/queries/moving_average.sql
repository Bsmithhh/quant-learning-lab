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
    