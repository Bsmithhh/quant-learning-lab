-- Find the 10 highest volume trading days across all tickers
-- Useful for identifying unusual market activity or liquidity events
SELECT
    ticker,
    date,
    close,
    volume
    FROM prices ORDER BY volume DESC LIMIT 10;