# Quantitative Trading System

Event-driven backtesting framework for systematic strategy evaluation.

**Built from scratch** to understand how production trading systems work:

- No external backtesting libraries
- Event queue with next-bar-open execution, so signals can't trade on the bar that produced them
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

**RiskAnalyzer** (`risk-analytics/`)

- Annualized return and volatility
- Sharpe ratio (risk-adjusted returns, 2% risk-free rate by default)
- Maximum drawdown (cumulative returns method)
- Value at Risk (95% confidence, historical)

**Backtesting Framework** (`backtesting/`)

- Single event queue: `MarketEvent → SignalEvent → OrderEvent → FillEvent`
- Strategy decides on day *t*'s close; ExecutionHandler fills at day *t+1*'s open
- Commission and slippage applied to both buys and sells
- Portfolio management (cash, positions, trades)
- DataHandler enforcing time constraints

See [`backtesting/README.md`](backtesting/README.md) for the event flow.

---

## Initial Results

**Strategy:** Moving Average Crossover (20/50), 100 shares per signal  
**Asset:** AAPL, 2023-01-01 → 2024-01-01  
**Costs:** $5 commission + 0.1% slippage per fill  
**Return:** +0.44% vs ~53% buy-and-hold over the same bars

| Metric (strategy equity curve) | Value |
|---|---|
| Trades executed | 1 (BUY signal Nov 14, filled Nov 15 open) |
| Annualized volatility | 0.83% |
| Sharpe ratio (rf = 2%) | −1.88 |
| Max drawdown | −0.55% |
| 95% daily VaR | −0.02% |

**Analysis:**

Strategy significantly underperformed due to:

- Late signal generation (single entry in November)
- High cash drag: in the market only ~1.5 of 12 months, and fixed 100-share sizing put at most ~19% of capital to work
- 50-day warm-up: no signal is possible until the 50th bar (mid-March), so the Feb 3 bullish crossover was missed (confirmed by the warm-up test below)
- No position management (couldn't sell when flat—SELL signal occurred before any BUY)

The low volatility and drawdown reflect a portfolio that was mostly cash, not a well-controlled strategy. The negative Sharpe means it earned less than the risk-free rate.

**Effect of the event-driven refactor:** Moving from same-close fills (old engine, +0.50%) to next-open fills with two-sided costs changed results by hundredths of a percent (2023: +0.50% → +0.44%; 2023–2024: +4.70% → +4.84%). Next-open timing can help or hurt depending on overnight gaps; costs always hurt.

**Key Insight:** System validates strategy weakness honestly: infrastructure works, strategy doesn't. This is the goal.

---

## External Validation - QuantConnect Deployment

**Date:** February 10, 2026  
**Strategy:** Moving Average Crossover (20/50)  
**Asset:** AAPL  
**Period:** Recorded as 2023-2024 for the QuantConnect run, though the results below match 2023 only (see open question). The local comparison was 2023.

### Results

**Local Backtest (yfinance data, 2023, original engine):**
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

The Aug 16 and Nov 14 crossovers match the local backtest exactly. The difference is the Feb 3 BUY, which let QuantConnect participate in the Feb–Aug rally.

My original hypothesis was that the two data sources differed. A warm-up test ruled that out.

### Warm-up test (`backtesting/examples/warmup_test.py`)

Same yfinance data and strategy, but the backtest loads history from June 2022 so the moving averages already exist on Jan 1, 2023. Signals before 2023 are suppressed.

| Local run (2023) | Signals | Return |
|---|---|---|
| No warm-up (data starts Jan 2023) | Aug 16 SELL, Nov 14 BUY | +0.44% |
| With warm-up (data from Jun 2022) | **Feb 3 BUY**, Aug 16 SELL, Nov 14 BUY | +2.88% |
| Same fills, fully invested, no costs | | **+19.15%** |

**Findings:**

1. **The Feb 3 crossover is in the yfinance data.** The original backtest couldn't see it because the 50-day MA doesn't exist until the 50th bar (Mar 16, 2023). On Feb 3 the 20-day MA (137.05) crossed above the 50-day MA (136.45). With warm-up, all three signal dates match QuantConnect exactly.
2. **The remaining return gap is position sizing.** The local strategy buys a fixed 100 shares (~15% of capital at the Feb 3 price). Investing the full portfolio on the same fills gives +19.15%, within 0.2 points of QuantConnect's +19.33%. The small residual is consistent with differences in costs and fill prices.

**Conclusion:** The 0.5% vs 19.33% gap came from indicator warm-up and position sizing, not data quality.

**Open question:** QuantConnect's three trades and its 19.33% return both match a 2023-only, fully invested run. I should confirm the QuantConnect algorithm's start/end dates and sizing call.

**Key Learning:** When two systems disagree, check setup assumptions first (warm-up, position sizing, date ranges, fill timing) before blaming the data.

---

## Technical Learnings

- Event-driven architecture prevents look-ahead bias
- Vectorized operations vs loops for performance
- Why simple technical strategies rarely work in practice
- Importance of defensive programming in financial systems
- Separation of concerns in system design

## Recent changes

- **Event-driven refactor:** Replaced the day-by-day loop with a single event queue and four event types. New ExecutionHandler fills orders at the next bar's open with commission and slippage on both sides. RiskAnalyzer now runs on the strategy's equity curve.
- **Transaction cost modeling and walk-forward validation:** Configurable commission per trade in Portfolio and Backtester; studied walk-forward validation concepts (sliding window, out-of-sample testing).

## Next Steps

- [x] Add transaction cost modeling
- [x] Event-driven execution with next-bar-open fills
- [x] Indicator warm-up test (data from mid-2022, trade from Jan 2023)
- [ ] Built-in warm-up period and percent-of-equity position sizing
- [ ] Implement position-aware strategy logic
- [x] Deploy on QuantConnect for external validation
- [ ] Add multiple strategy comparison
- [ ] Parameter optimization framework

---

## Disclaimer

Projects in this repository are for educational and research purposes only and do not constitute investment advice. Past performance does not guarantee future results.
