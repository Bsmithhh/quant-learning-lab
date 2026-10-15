# Backtester orchestrator: a single event queue drives every component.
from collections import deque
import pandas as pd
from .data_handler import DataHandler
from .strategy import Strategy
from .portfolio import Portfolio
from .execution import ExecutionHandler
from .events import MarketEvent, SignalEvent, OrderEvent, FillEvent


class Backtester:
    def __init__(self, strategy, data, ticker: str, initial_cash: float = 100000,
                 commission: float = 5, slippage_pct: float = 0.001):
        """
            Initialize backtester.

            Args:
                strategy: Strategy instance
                data: DataFrame with lowercase 'open' and 'close' columns
                ticker: Symbol being traded
                initial_cash: Starting cash
                commission: Flat fee per fill
                slippage_pct: Fraction of price lost on every fill
        """
        self.strategy = strategy
        self.data = data
        self.ticker = ticker
        self.initial_cash = initial_cash
        self.data_handler = DataHandler(self.data)
        self.portfolio = Portfolio(self.initial_cash)
        self.execution = ExecutionHandler(commission, slippage_pct)
        self.events = deque()
        self.results: list = []

    def run(self):
        """
        Run the backtest.

        Each day:
          1. MarketEvent: fill yesterday's orders at today's open, then ask
             the strategy for a signal using data up to today's close.
          2. SignalEvent -> Portfolio decides whether to place an order.
          3. OrderEvent -> ExecutionHandler holds it until tomorrow's open.
          4. FillEvent -> Portfolio updates cash and positions.

        Returns:
            List of daily results
        """
        for current_date in self.data_handler.data.index:
            self.events.append(MarketEvent(current_date))

            while self.events:
                event = self.events.popleft()

                if isinstance(event, MarketEvent):
                    open_price = self.data.loc[event.date, 'open']
                    for fill in self.execution.fill_pending(event.date, open_price):
                        self.events.append(fill)
                    historical_data = self.data_handler.get_data_up_to(event.date)
                    signal = self.strategy.generate_signal(historical_data)
                    if signal['action'] != 'HOLD':
                        self.events.append(SignalEvent(event.date, self.ticker, signal['action'], signal['quantity']))

                elif isinstance(event, SignalEvent):
                    order = self.portfolio.on_signal(event)
                    if order is not None:
                        self.events.append(order)

                elif isinstance(event, OrderEvent):
                    self.execution.submit(event)

                elif isinstance(event, FillEvent):
                    try:
                        self.portfolio.on_fill(event)
                    except ValueError:
                        pass  # e.g. not enough cash at the fill price

            # Value the portfolio at today's close, after all of today's events
            temp_df = self.data_handler.get_data_up_to(current_date).copy()
            temp_df['ticker'] = self.ticker
            self.results.append({
                'date': current_date,
                'portfolio_value': self.portfolio.get_value(temp_df),
                'current_cash': self.portfolio.cash,
                'signal': signal,
                'portfolio': self.portfolio.positions.copy()
            })
        return self.results

    def equity_curve(self) -> pd.Series:
        """Daily portfolio value indexed by date. Call after run()."""
        return pd.DataFrame(self.results).set_index('date')['portfolio_value']
