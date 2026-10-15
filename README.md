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
- 50-day warm-up: no signal is possible until the 50th bar (mid-March), so any earlier crossover is missed
- No position management (couldn't sell when flat—SELL signal occurred before any BUY)

The low volatility and drawdown reflect a portfolio that was mostly cash, not a well-controlled strategy. The negative Sharpe means it earned less than the risk-free rate.

**Effect of the event-driven refactor:** Moving from same-close fills (old engine, +0.50%) to next-open fills with two-sided costs changed results by hundredths of a percent (2023: +0.50% → +0.44%; 2023–2024: +4.70% → +4.84%). Next-open timing can help or hurt depending on overnight gaps; costs always hurt.

**Key Insight:** System validates strategy weakness honestly: infrastructure works, strategy doesn't. This is the goal.

---

## External Validation - QuantConnect Deployment

**Date:** February 10, 2026  
**Strategy:** Moving Average Crossover (20/50)  
**Asset:** AAPL  
**Period:** 2023-2024 (QuantConnect run). The local comparison below was 2023 only.

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

Two candidate explanations:

1. **Indicator warm-up (leading hypothesis, not yet confirmed).** The local backtest starts with no price history before Jan 2023, so the 50-day MA doesn't exist until mid-March. A Feb 3 crossover is impossible locally regardless of the data. QuantConnect typically warms indicators up with history from before the start date.
2. **Data source differences.** The original hypothesis. It's less likely given that the other two crossover dates match exactly.

The two runs also covered different periods (2023–2024 vs. 2023), so the returns aren't directly comparable.

**Planned test:** Load data from mid-2022, start trading Jan 1, 2023, and check whether a Feb 3 BUY appears locally.

**Key Learning:** When two systems disagree, check assumptions about setup first (warm-up, date ranges, fill timing) before blaming the data.

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
- [ ] Indicator warm-up test (data from mid-2022, trade from Jan 2023)
- [ ] Implement position-aware strategy logic
- [x] Deploy on QuantConnect for external validation
- [ ] Add multiple strategy comparison
- [ ] Parameter optimization framework

---

## Disclaimer

Projects in this repository are for educational and research purposes only and do not constitute investment advice. Past performance does not guarantee future results.
