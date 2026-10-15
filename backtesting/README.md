# Backtesting Framework

Event-driven execution engine for strategy simulation. A single event queue passes four event types between components. The strategy decides on a bar's close, and orders fill at the next bar's open, so no trade uses a price that wasn't available when the decision was made.

## Event Flow

```
MarketEvent   new bar for day t
   │  ExecutionHandler fills orders pending from day t-1 at day t's open → FillEvent
   │  Strategy sees data up to day t's close
   ▼
SignalEvent   strategy wants to BUY/SELL
   ▼
OrderEvent    Portfolio approved it (e.g. not selling shares it doesn't own)
   ▼          ExecutionHandler holds it until day t+1
FillEvent     filled at day t+1's open, with slippage and commission
   ▼
Portfolio updates cash and positions
```

Each day the Backtester pushes one `MarketEvent` and processes the queue until it's empty, then values the portfolio at that day's close.

## Components

### Events (`events.py`)

Four dataclasses that carry information and contain no logic: `MarketEvent(date)`, `SignalEvent`, `OrderEvent` (both `date, ticker, action, quantity`), and `FillEvent` (adds `fill_price` and `commission`).

### DataHandler

Time-aware data access for the backtest loop.

- **Role:** Returns only historical data available at each simulation date.
- **`get_data_up_to(date)`:** Slices the dataset so that `date` and all rows before it are included; nothing after. Enforces temporal constraints and prevents look-ahead.
- **Validation:** Rejects `None` or empty datasets at construction; raises if requested date is outside the data range.

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

- **`on_signal(signal)`:** Turns a `SignalEvent` into an `OrderEvent`, or returns `None` for a SELL when there aren't enough shares.
- **`on_fill(fill)`:** Applies a `FillEvent` by calling `buy` or `sell` at the fill price and commission.
- **Cash:** Tracks balance; `buy` raises `ValueError` if cash is insufficient at the fill price (the Backtester skips that fill).
- **Positions:** Dict of ticker → share count (multi-ticker capable).
- **Trades:** List of executed trades (ticker, action, quantity, price, cost/gain).
- **`get_value(df)`:** Values the portfolio using the latest close per ticker from the given DataFrame plus cash.

### ExecutionHandler (`execution.py`)

Simulated broker.

- **`submit(order)`:** Holds the order; nothing fills on the bar that created it.
- **`fill_pending(date, open_price)`:** Called at the start of the next bar. Fills every pending order at that bar's open and clears the list.
- **Costs:** Flat `commission` per fill (default $5). `slippage_pct` (default 0.1%) always works against the trade: buys pay `open × (1 + slippage)`, sells receive `open × (1 − slippage)`.
- A signal on the final bar never fills, because there is no next open.

### Backtester

Owns the event queue (`collections.deque`) and routes each event to the right component.

- **Input:** DataFrame with lowercase `open` (fills) and `close` (signals, valuation) columns.
- **Output:** `run()` returns a list of daily result dicts (date, portfolio value, cash, signal, positions). `equity_curve()` returns portfolio value as a date-indexed Series, ready for `RiskAnalyzer`.

Run `backtesting/examples/first_backtest.py` for a full demo.

## Usage

```python
from data_processing.market_data_processor import MarketDataProcessor
from backtesting.strategy import MovingAverageCrossover
from backtesting.backtester import Backtester

# Get data. Use adjusted prices for both open and close so they're consistent.
mdp = MarketDataProcessor("AAPL", "2023-01-01", "2024-01-01")
data = mdp.build().copy()
data["close"] = data["Adj Close"]
data["open"] = data["Open"] * data["Adj Close"] / data["Close"]

# Create strategy and backtester
strategy = MovingAverageCrossover(short_window=20, long_window=50, quantity=100)
bt = Backtester(strategy=strategy, data=data, ticker='AAPL', initial_cash=100000,
                commission=5, slippage_pct=0.001)
bt.run()

# Analyze
equity = bt.equity_curve()
print(f"Total Return: {equity.iloc[-1] / 100000 - 1:.2%}")
print(f"Trades executed: {len(bt.portfolio.trades)}")
```

For risk metrics, pass `equity.pct_change().dropna()` to `RiskAnalyzer` (see the example script).

## Example Results (AAPL 2023-01-01 → 2024-01-01)

- **Strategy:** MovingAverageCrossover (20/50), 100 shares per signal, $5 commission + 0.1% slippage per fill
- **Starting value:** $100,000 → **Ending value:** ~$100,439 (**+0.44%**)
- **Trades executed:** 1 (BUY signal on Nov 14 close, filled at Nov 15 open; one earlier SELL signal did not execute—see below)
- **Sharpe (rf = 2%):** −1.88 · **Max drawdown:** −0.55%
- **Equity curve:** `backtesting/examples/backtest_equity_curve.png`

The previous engine filled at the signal bar's close and reported +0.50%. The difference comes from next-open timing and two-sided slippage.

**Underperformance vs buy-and-hold:** The MA crossover is a lagging indicator and often enters/exits late. In this period the first crossover was a *bearish* one (SELL) before any position was opened; the only executed trade was a later BUY. Honest backtesting like this is the basis for improving or replacing the strategy.

**"Can't sell when flat":** Signal order matters. If the strategy emits **SELL** before any **BUY** (e.g. 20-MA crossed below 50-MA early in the year), `Portfolio.on_signal` returns no order and the signal is dropped. So you may see 1 BUY and 1 SELL *signal* but only 1 *executed* trade when the SELL came first. The example script prints signal dates and positions so you can verify.
