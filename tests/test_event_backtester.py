# Tests for event-driven execution timing and costs

import pandas as pd
import pytest
from backtesting.backtester import Backtester
from backtesting.execution import ExecutionHandler
from backtesting.portfolio import Portfolio
from backtesting.events import OrderEvent, SignalEvent


class SignalOnDates:
    """Test strategy: emits a given action on given dates, HOLD otherwise."""

    def __init__(self, actions: dict, quantity: int = 10):
        self.actions = actions  # {date string: 'BUY' or 'SELL'}
        self.quantity = quantity

    def generate_signal(self, data):
        today = data.index[-1].strftime('%Y-%m-%d')
        if today in self.actions:
            return {'action': self.actions[today], 'quantity': self.quantity}
        return {'action': 'HOLD', 'quantity': 0}


def make_data():
    # Opens and closes differ every day, so a fill at the wrong price is obvious
    idx = pd.date_range("2023-01-02", periods=5, freq="B")
    return pd.DataFrame(
        {"open": [100.0, 110.0, 120.0, 130.0, 140.0],
         "close": [105.0, 115.0, 125.0, 135.0, 145.0]},
        index=idx,
    )


def test_signal_on_day_t_fills_at_day_t_plus_1_open():
    data = make_data()
    strategy = SignalOnDates({"2023-01-03": "BUY"})  # day t = Jan 3
    bt = Backtester(strategy, data, "TEST", initial_cash=10000, commission=0, slippage_pct=0)
    results = bt.run()

    # No shares on day t itself: the order is still waiting for tomorrow
    assert results[1]['portfolio'].get("TEST", 0) == 0
    # Filled on day t+1 (Jan 4) at that day's open, not day t's close (115)
    assert results[2]['portfolio']["TEST"] == 10
    assert bt.portfolio.trades[0]['price'] == 120.0


def test_slippage_and_commission_hit_buys_and_sells():
    data = make_data()
    strategy = SignalOnDates({"2023-01-02": "BUY", "2023-01-04": "SELL"})
    bt = Backtester(strategy, data, "TEST", initial_cash=10000, commission=5, slippage_pct=0.01)
    bt.run()

    buy, sell = bt.portfolio.trades
    assert buy['price'] == pytest.approx(110.0 * 1.01)   # paid above Jan 3 open
    assert sell['price'] == pytest.approx(130.0 * 0.99)  # received below Jan 5 open
    assert buy['cost'] == pytest.approx(10 * 110.0 * 1.01 + 5)
    assert sell['gain'] == pytest.approx(10 * 130.0 * 0.99 - 5)


def test_signal_on_last_day_never_fills():
    data = make_data()
    strategy = SignalOnDates({"2023-01-06": "BUY"})  # last bar: no next open
    bt = Backtester(strategy, data, "TEST", initial_cash=10000)
    bt.run()
    assert bt.portfolio.trades == []


def test_portfolio_rejects_sell_when_flat():
    portfolio = Portfolio(initial_cash=10000)
    signal = SignalEvent(pd.Timestamp("2023-01-02"), "TEST", "SELL", 10)
    assert portfolio.on_signal(signal) is None


def test_execution_handler_clears_orders_after_filling():
    handler = ExecutionHandler(commission=0, slippage_pct=0)
    handler.submit(OrderEvent(pd.Timestamp("2023-01-02"), "TEST", "BUY", 10))
    fills = handler.fill_pending(pd.Timestamp("2023-01-03"), 100.0)
    assert len(fills) == 1
    assert fills[0].fill_price == 100.0
    assert handler.fill_pending(pd.Timestamp("2023-01-04"), 101.0) == []
