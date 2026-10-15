"""
Warm-up test: does pre-2023 history produce the Feb 3, 2023 crossover
that QuantConnect found and the original local backtest missed?

Run from project root: python backtesting/examples/warmup_test.py
"""
import sys
sys.path.insert(0, ".")

import pandas as pd
from data_processing.market_data_processor import MarketDataProcessor
from backtesting.strategy import MovingAverageCrossover
from backtesting.backtester import Backtester

TRADE_START = pd.Timestamp("2023-01-01")


class TradeFrom(MovingAverageCrossover):
    """Sees all history so the MAs are warmed up, but only signals from TRADE_START."""

    def generate_signal(self, data):
        signal = super().generate_signal(data)
        if data.index[-1] < TRADE_START:
            return {'action': 'HOLD', 'quantity': 0}
        return signal


def run(start, strategy):
    data = MarketDataProcessor("AAPL", start, "2024-01-01").build().copy()
    data["close"] = data["Adj Close"]
    data["open"] = data["Open"] * data["Adj Close"] / data["Close"]
    bt = Backtester(strategy, data, "AAPL", initial_cash=100000)
    bt.run()
    signals = [(r['date'].date(), r['signal']['action']) for r in bt.results
               if r['signal']['action'] != 'HOLD']
    equity = bt.equity_curve()
    print(f"\nData from {start}:")
    print(f"  Signals: {signals}")
    print(f"  Return:  {equity.iloc[-1] / 100000 - 1:.2%}")
    return bt


run("2023-01-01", MovingAverageCrossover(20, 50, 100))
bt = run("2022-06-01", TradeFrom(20, 50, 100))

# QuantConnect algorithms typically invest the whole portfolio on each signal.
# Compound the fill-to-fill price moves to see what fully invested would return.
growth = 1.0
trades = bt.portfolio.trades
last_close = bt.data["close"].iloc[-1]
for i in range(0, len(trades), 2):
    buy = trades[i]['price']
    sell = trades[i + 1]['price'] if i + 1 < len(trades) else last_close
    growth *= sell / buy
print(f"\nFully invested on the same fills (no costs): {growth - 1:.2%}")
