"""
Demo: MovingAverageCrossover + DataHandler with live AAPL data.
Run from project root: python backtesting/examples/simple_backtest.py
"""
import sys
sys.path.insert(0, ".")

from backtesting.strategy import MovingAverageCrossover
from backtesting.data_handler import DataHandler
from data_processing.market_data_processor import MarketDataProcessor

# Get data
mdp = MarketDataProcessor("AAPL", "2023-01-01", "2024-01-01")
full_data = mdp.build()

# Strategy expects lowercase 'close' (use Adj Close for backtesting)
full_data = full_data.copy()
full_data["close"] = full_data["Adj Close"]

# Create strategy and data handler
strategy = MovingAverageCrossover(short_window=20, long_window=50, quantity=100)
dh = DataHandler(full_data)

# Strategy only signals on the exact day of a crossover. Scan every trading day
# (from day 50 onward) to find BUY/SELL; sampling a few dates usually misses them.
print("=== Crossover signals (every trading day) ===")
buys, sells = [], []
for i in range(strategy.long_window, len(full_data)):
    date = full_data.index[i]
    data_up_to = dh.get_data_up_to(date)
    sig = strategy.generate_signal(data_up_to)
    if sig["action"] == "BUY":
        buys.append(date)
        print(f"  BUY  @ {date.date()}")
    elif sig["action"] == "SELL":
        sells.append(date)
        print(f"  SELL @ {date.date()}")
print(f"Total: {len(buys)} BUY, {len(sells)} SELL")

# Would we have been profitable? (start in cash; BUY = go long, SELL = go to cash)
close = full_data["close"]
start_price = close.iloc[0]
end_price = close.iloc[-1]
# Strategy: in cash until first BUY, then long until next SELL, etc. In 2023: SELL first (no position), then BUY Nov 14 -> long to end.
buy_and_hold_return = (end_price - start_price) / start_price
if buys:
    first_buy_date = buys[0]
    last_buy_date = buys[-1]
    price_at_first_buy = close.loc[close.index <= first_buy_date].iloc[-1]
    price_at_last_buy = close.loc[close.index <= last_buy_date].iloc[-1]
    # Simple: we only went long at last BUY (Nov 14); hold to end.
    strategy_return = (end_price - price_at_last_buy) / price_at_last_buy
else:
    strategy_return = 0.0
print("\n=== Profitability (start in cash) ===")
print(f"Buy-and-hold (full period):     {buy_and_hold_return:.2%}")
print(f"Strategy (long from last BUY):   {strategy_return:.2%}")
print(f"Strategy profitable?             {strategy_return > 0}")
print(f"Strategy vs buy-and-hold:        {'underperformed' if strategy_return < buy_and_hold_return else 'outperformed'} in this period")

# Sample a few dates (for reference; most will be HOLD)
print("\n=== Sample dates ===")
for date in ["2023-06-01", "2023-08-16", "2023-11-14", "2023-12-01"]:
    data_up_to = dh.get_data_up_to(date)
    if len(data_up_to) < strategy.long_window:
        print(f"{date}: skipped (need {strategy.long_window} days)")
        continue
    signal = strategy.generate_signal(data_up_to)
    print(f"{date}: {signal}")

# Optional: visualize MAs and crossover points
def _plot_ma_sanity():
    import matplotlib.pyplot as plt
    data = full_data.copy()
    data["ma_20"] = data["close"].rolling(20).mean()
    data["ma_50"] = data["close"].rolling(50).mean()
    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data["close"], label="Close", alpha=0.5)
    plt.plot(data.index, data["ma_20"], label="20-day MA")
    plt.plot(data.index, data["ma_50"], label="50-day MA")
    plt.legend()
    plt.title("AAPL: Price and Moving Averages")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__" and "--plot" in sys.argv:
    _plot_ma_sanity()
