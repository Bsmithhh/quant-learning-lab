# SQL Analytics

Financial time-series queries using SQLite and window functions.

## Queries

### Moving Average (`moving_average.sql`)
Calculates 20-day simple moving average using window functions.
Demonstrates: `PARTITION BY`, `ORDER BY`, `ROWS BETWEEN`

### Daily Returns (`daily_returns.sql`)
Computes daily percentage returns using LAG function.
Demonstrates: `LAG()`, CTE pattern

### Top Volume Days (`volume_rankings.sql`)
Identifies highest volume trading days across all tickers.
Demonstrates: `ORDER BY`, `LIMIT`

### Gap Detection (`gap_detection.sql`)
Finds days where opening price significantly differed from previous close.
Demonstrates: `LAG()` with `WHERE` filtering, absolute value functions

## Usage

Queries can be executed via Python:
```python
import sqlite3
import pandas as pd

conn = sqlite3.connect("data/market_data.db")
with open("sql_analytics/queries/moving_average.sql") as f:
    result = pd.read_sql_query(f.read(), conn)
conn.close()
```
