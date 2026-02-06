# Backtesting

Event-driven backtesting framework for trading strategies.

### Strategy Layer

Base Strategy class defines interface for all trading strategies.

**MovingAverageCrossover:**
- Generates BUY signal when short MA crosses above long MA
- Generates SELL signal when short MA crosses below long MA
- Configurable windows (default 20/50 days)
- Returns HOLD when insufficient data or no crossover

### Portfolio

Manages cash, positions, and trade execution.

**Features:**
- Cash tracking with validation
- Multi-ticker position management
- Buy/sell execution with sufficient funds/shares checks
- Trade history recording
- Portfolio valuation using current prices

### Backtester

Orchestrates data, strategy, and portfolio in an event-driven loop. Run `backtesting/examples/first_backtest.py` for a full demo.

### First backtest results (AAPL 2023-01-01 → 2024-01-01)

- **Strategy:** MovingAverageCrossover (20/50), 100 shares per signal
- **Starting value:** $100,000 → **Ending value:** ~$100,500 (**+0.5%**)
- **Trades executed:** 1 (one BUY; one SELL signal did not execute—see below)
- **Equity curve:** `backtesting/examples/backtest_equity_curve.png`

**Underperformance vs buy-and-hold:** The MA crossover is a lagging indicator and often enters/exits late. In this period the first crossover was a *bearish* one (SELL) before any position was opened; the only executed trade was a later BUY. Honest backtesting like this is the basis for improving or replacing the strategy.

**"Can't sell when flat":** Signal order matters. If the strategy emits **SELL** before any **BUY** (e.g. 20-MA crossed below 50-MA early in the year), the backtester tries to sell with 0 shares; `Portfolio.sell` raises and the trade is skipped. So you may see 1 BUY and 1 SELL *signal* but only 1 *executed* trade when the SELL came first. The example script prints signal dates and positions so you can verify.