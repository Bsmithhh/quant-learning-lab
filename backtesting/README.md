# Backtesting Framework

Event-driven execution engine for strategy simulation. Prevents look-ahead bias by advancing day-by-day and exposing only data available at each point in time.

## Components

### DataHandler

Time-aware data access for the backtest loop.

- **Role:** Returns only historical data available at each simulation date.
- **`get_data_up_to(date)`:** Slices the dataset so that `date` and all rows before it are included; nothing after. Enforces temporal constraints and prevents look-ahead.
- **Validation:** Rejects `None` or empty datasets at construction; raises if requested date is outside the data range.

Used by the Backtester each day to pass the correct history to the strategy.

### Strategy

Signal generation interface. Base contract: subclasses implement `generate_signal(data)` and return a dict with `action` (BUY/SELL/HOLD) and `quantity`.

**MovingAverageCrossover:**

- Short MA (default 20) and long MA (default 50) on close price.
- **BUY** when short MA crosses above long MA.
- **SELL** when short MA crosses below long MA.
- **HOLD** when there is insufficient data (fewer than `long_window` rows) or no crossover.
- Configurable `quantity` per signal (default 100 shares).
- Uses `.copy()` on input data so the original series is not mutated.

### Portfolio

Cash and position management with trade recording.

- **Cash:** Tracks balance; validates sufficient cash on buy and sufficient shares on sell.
- **Positions:** Dict of ticker → share count (multi-ticker capable).
- **Trades:** List of executed trades (ticker, action, quantity, price, cost/gain).
- **`get_value(df)`:** Values the portfolio using the latest close per ticker from the given DataFrame plus cash.

Raises `ValueError` on invalid buy (not enough cash) or sell (not enough shares). The Backtester catches these and skips the trade (e.g. SELL when flat).

### Backtester

Orchestration engine that runs the event-driven loop.

- **Setup:** Wraps input data in a `DataHandler`, creates a `Portfolio` with initial cash, and holds a `Strategy` and ticker.
- **Loop:** For each trading day, gets historical data up to that day, asks the strategy for a signal, executes buy/sell against the portfolio (catching validation errors), then records a snapshot (date, portfolio value, cash, signal, positions).
- **Output:** Returns a list of daily result dicts; can be turned into a DataFrame for analysis and equity curves.

Run `backtesting/examples/first_backtest.py` for a full demo.

## Usage

```python
from data_processing.market_data_processor import MarketDataProcessor
from backtesting.strategy import MovingAverageCrossover
from backtesting.backtester import Backtester
import pandas as pd

# Get data (strategy expects lowercase 'close')
mdp = MarketDataProcessor("AAPL", "2023-01-01", "2024-01-01")
data = mdp.build()
data = data.copy()
data["close"] = data["Adj Close"]

# Create strategy and backtester
strategy = MovingAverageCrossover(short_window=20, long_window=50, quantity=100)
bt = Backtester(strategy=strategy, data=data, ticker='AAPL', initial_cash=100000)
results = bt.run()

# Analyze
results_df = pd.DataFrame(results)
print(f"Total Return: {(results_df['portfolio_value'].iloc[-1] / 100000 - 1):.2%}")
print(f"Trades executed: {len(bt.portfolio.trades)}")
```

## Example Results (AAPL 2023-01-01 → 2024-01-01)

- **Strategy:** MovingAverageCrossover (20/50), 100 shares per signal  
- **Starting value:** $100,000 → **Ending value:** ~$100,500 (**+0.5%**)  
- **Trades executed:** 1 (one BUY; one SELL signal did not execute—see below)  
- **Equity curve:** `backtesting/examples/backtest_equity_curve.png`

**Underperformance vs buy-and-hold:** The MA crossover is a lagging indicator and often enters/exits late. In this period the first crossover was a *bearish* one (SELL) before any position was opened; the only executed trade was a later BUY. Honest backtesting like this is the basis for improving or replacing the strategy.

**"Can't sell when flat":** Signal order matters. If the strategy emits **SELL** before any **BUY** (e.g. 20-MA crossed below 50-MA early in the year), the backtester tries to sell with 0 shares; `Portfolio.sell` raises and the trade is skipped. So you may see 1 BUY and 1 SELL *signal* but only 1 *executed* trade when the SELL came first. The example script prints signal dates and positions so you can verify.
