# Integration tests for backtester and related components

import pytest
import pandas as pd
from backtesting.backtester import Backtester
from backtesting.strategy import MovingAverageCrossover
from backtesting.portfolio import Portfolio
from backtesting.data_handler import DataHandler


def test_backtester_completes():
    """Backtester runs without errors and returns non-empty results."""
    # Synthetic data: enough rows for 50-day MA, with close and Adj Close
    idx = pd.date_range("2023-01-01", periods=100, freq="B")
    data = pd.DataFrame(
        {
            "close": 100.0 + (pd.Series(range(100)) * 0.5),
            "Adj Close": 100.0 + (pd.Series(range(100)) * 0.5),
        },
        index=idx,
    )
    strategy = MovingAverageCrossover(short_window=20, long_window=50, quantity=10)
    bt = Backtester(strategy=strategy, data=data, ticker="TEST", initial_cash=10000)
    results = bt.run()
    assert len(results) > 0
    assert all("date" in r and "portfolio_value" in r for r in results)


def test_initial_cash():
    """Portfolio starts with correct cash and empty positions."""
    portfolio = Portfolio(initial_cash=100000)
    assert portfolio.cash == 100000
    assert portfolio.positions == {}
    assert len(portfolio.trades) == 0


def test_buy_updates_cash():
    """Buy reduces cash and updates positions correctly."""
    portfolio = Portfolio(initial_cash=100000)
    portfolio.buy("AAPL", 100, 150)
    assert portfolio.cash == 85000
    assert portfolio.positions["AAPL"] == 100
    assert len(portfolio.trades) == 1
    assert portfolio.trades[0]["action"] == "BUY"
    assert portfolio.trades[0]["cost"] == 15000


def test_no_lookahead():
    """DataHandler returns only data up to cutoff; no future data."""
    idx = pd.date_range("2023-01-01", periods=100, freq="B")
    df = pd.DataFrame({"Close": [100.0] * 100, "Adj Close": [100.0] * 100}, index=idx)
    dh = DataHandler(df)
    # Cutoff inside range: data ends ~May 19; use March 1 so we have a clear "future"
    out = dh.get_data_up_to("2023-03-01")
    assert out.index.max() <= pd.Timestamp("2023-03-01")
    # No April data (future relative to cutoff)
    april_or_later = out.index[out.index >= pd.Timestamp("2023-04-01")]
    assert len(april_or_later) == 0
