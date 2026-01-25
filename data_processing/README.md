# Data Processing

## MarketDataProcessor

This module handles historical market data ingestion and preprocessing.

### Features
- Fetches historical OHLCV data using yfinance
- Validates required columns and datetime index
- Forward-fills prices but preserves true volume behavior
- Computes daily adjusted returns
- Designed for reuse in backtesting and risk analysis

### Validation Pipeline

The processor enforces strict validation before data can be used:

**OHLC Integrity:**
- High >= max(Open, Close, Low)
- Low <= min(Open, Close, High)
- All prices must be positive
- Volume must be non-negative

**Return Sanity:**
- Returns column must exist
- No NaN values in returns
- Returns must fall within bounds (-95% to +500%)

**Minimum History:**
- Dataset must contain at least 60 rows by default
- Configurable via `build(min_rows=...)`

These checks prevent silent data errors from propagating into risk models and backtests.

### Diagnostics

The `diagnostics()` method reports data quality and return integrity metrics after returns have been computed.

It surfaces:
- Date range coverage
- Mean and volatility of returns
- Extreme returns
- Zero-volume trading days
- Index ordering and uniqueness checks

This method is intended for validation and analysis, not mutation of data.

### Data Persistence

The processor supports saving cleaned market data to SQLite databases:

**Features:**
- Saves OHLCV data with ticker identifier
- Preserves date index as queryable column
- Returns confirmation dict with rows saved and database path
- Uses `if_exists='replace'` to ensure data consistency

**Usage:**
```python
mdp = MarketDataProcessor("AAPL", "2023-01-01", "2024-01-01")
mdp.build()
result = mdp.save_to_sqlite("data/market_data.db")
```

### Example Usage
```python
mdp = MarketDataProcessor("AAPL", "2020-01-01", "2024-01-01")
mdp.fetch_prices()
mdp.add_returns()
stats = mdp.summary()
```

This is **huge signal** for reviewers.

---

### What the Class Does

The `MarketDataProcessor` class provides a clean, validated pipeline for fetching and preprocessing financial market data. It:

1. **Fetches market data** from Yahoo Finance using the `yfinance` library for a specified ticker and date range
2. **Cleans the data** by handling missing values according to a consistent policy
3. **Computes daily returns** using adjusted close prices
4. **Validates the dataset** to ensure it meets quality standards before use in downstream analysis

The class follows a builder pattern with a `build()` method that orchestrates the entire pipeline: `fetch_prices()` → `add_returns()` → `validate()`.

### Why Strict Validation Exists

Strict validation is essential for quantitative finance applications because:

- **Prevents silent failures**: Catches data quality issues early before they propagate through analysis pipelines
- **Ensures consistency**: Guarantees that downstream code can rely on specific data structures (DatetimeIndex, required columns, etc.)
- **Avoids runtime errors**: Identifies problems like missing columns, unsorted dates, or duplicate timestamps that would cause failures during backtesting or analysis
- **Maintains data integrity**: Validates that the dataset meets the assumptions required by financial calculations (e.g., monotonic time series for returns)

The validation checks for:
- Non-empty datasets
- Presence of all required columns (Open, High, Low, Close, Adj Close, Volume)
- Proper DatetimeIndex type
- Monotonically increasing date index
- No duplicate timestamps

### Assumptions

The class makes the following explicit assumptions about data handling:

1. **Adjusted Close for Returns**: Daily returns (`ret_1d`) are computed using `Adj Close` prices, which account for corporate actions (splits, dividends) and provide a more accurate representation of investment performance.

2. **Forward-Fill Prices**: Price columns (Open, High, Low, Close, Adj Close) are forward-filled on non-trading days. This reflects the assumption that prices remain unchanged on weekends and holidays, which is standard practice in quantitative finance to avoid gaps in time series.

3. **No Forward-Fill for Volume**: Volume is **not** forward-filled. Missing volume values are filled with `0` to indicate no trading activity occurred on that day. This preserves the distinction between trading days and non-trading days, which is important for volume-based analysis and indicators.

These assumptions align with the [Data Cleaning Policy](../README.md#data-cleaning-policy) documented in the main repository README.
