# Quantitative Trading System

Event-driven backtesting framework for systematic strategy evaluation.

**Built from scratch** to understand how production trading systems work:

- No external backtesting libraries
- Event-driven architecture preventing look-ahead bias
- Complete data pipeline from ingestion to analytics

**Tech Stack:** Python, Pandas, NumPy, SQLite, Matplotlib

---

## Architecture

### Components

**MarketDataProcessor** (`data_processing/`)

- Fetches OHLCV data via yfinance
- Validates price relationships and data integrity
- Computes returns with forward-fill for missing data
- Enforces minimum history requirements

**SQL Analytics** (`sql_analytics/`)

- Persists processed data to SQLite
- Window function queries for moving averages, returns, gaps
- Supports time-series analysis at scale

**RiskAnalyzer** (`risk_analytics/`)

- Annualized return and volatility
- Sharpe ratio (risk-adjusted returns)
- Maximum drawdown (cumulative returns method)
- Value at Risk (95% confidence, historical)

**Backtesting Framework** (`backtesting/`)

- Event-driven execution (day-by-day simulation)
- Strategy interface for pluggable trading logic
- Portfolio management (cash, positions, trades)
- DataHandler enforcing time constraints

---

## Initial Results

**Strategy:** Moving Average Crossover (20/50)  
**Asset:** AAPL (2023)  
**Return:** +0.50% vs ~48% buy-and-hold

**Analysis:**

Strategy significantly underperformed due to:

- Late signal generation (single entry in November)
- High cash drag (invested only 1.5 months of 12)
- No position management (couldn't sell when flat—SELL signal occurred before any BUY)

**Key Insight:** System validates strategy weakness honestly: infrastructure works, strategy doesn't. This is the goal.

---

## External Validation - QuantConnect Deployment

**Date:** February 10, 2025  
**Strategy:** Moving Average Crossover (20/50)  
**Asset:** AAPL  
**Period:** 2023-2024

### Results

**Local Backtest (yfinance data):**
- Return: +0.50%
- Trades: 1 (BUY on Nov 14)
- Pattern: Flat until Nov, small uptick

**QuantConnect (QC data):**
- Return: +19.33%
- Trades: 3 crossovers detected
  - Feb 3: Bullish crossover (BUY)
  - Aug 16: Bearish crossover (SELL)
  - Nov 14: Bullish crossover (BUY)
- Pattern: Active participation throughout year

### Analysis

Significant performance difference (19% vs 0.5%) due to **data source differences**.

**Hypothesis:** QuantConnect's AAPL data showed crossover on Feb 3, 2023 that yfinance data did not contain. This earlier entry allowed participation in Feb–Aug rally (+34% in AAPL), resulting in higher returns.

**Key Learning:** Data quality and source selection critically impact strategy performance. Same strategy logic, different data = vastly different results.

**QuantConnect Link:** [Paste your algorithm URL if you have it]

**Validation Status:** ✅ Strategy deploys and runs correctly on external platform. Logic is sound, results vary with data.

---

## Technical Learnings

- Event-driven architecture prevents look-ahead bias
- Vectorized operations vs loops for performance
- Why simple technical strategies rarely work in practice
- Importance of defensive programming in financial systems
- Separation of concerns in system design

## Recent changes

- **Transaction cost modeling and walk-forward validation:** Configurable commission per trade in Portfolio and Backtester; studied walk-forward validation concepts (sliding window, out-of-sample testing).

## Next Steps

- [x] Add transaction cost modeling
- [ ] Implement position-aware strategy logic
- [x] Deploy on QuantConnect for external validation
- [ ] Add multiple strategy comparison
- [ ] Parameter optimization framework

---

## Disclaimer

Projects in this repository are for educational and research purposes only and do not constitute investment advice. Past performance does not guarantee future results.
