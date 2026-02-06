# Backtester orchestrator goes here
import pandas as pd
from .data_handler import DataHandler
from .strategy import Strategy
from .portfolio import Portfolio

class Backtester:
    def __init__(self, strategy, data, ticker: str, initial_cash: float = 100000):
        """
            Initialize backtester.
            
            Args:
                strategy: Strategy instance
                data: Full DataFrame (from MarketDataProcessor)
                ticker: Symbol being traded
                initial_cash: Starting cash
        """
        self.strategy = strategy
        self.data = data
        self.ticker = ticker
        self.initial_cash = initial_cash
        self.data_handler = DataHandler(self.data)
        self.portfolio = Portfolio(self.initial_cash)
        self.results:list = []

    def run(self):
        """
        Run the backtest.
        
        Returns:
            List of daily results
        """
        dates = self.data_handler.data.index
        for current_date in dates:
            historical_data = self.data_handler.get_data_up_to(current_date)
            temp_df = historical_data.copy()
            temp_df['ticker'] = self.ticker
            signal = self.strategy.generate_signal(historical_data)
            current_price = historical_data.loc[current_date, 'Adj Close']
            quantity = signal['quantity']
            if signal['action'] == 'BUY':
                try:
                    self.portfolio.buy(self.ticker, quantity, current_price)
                except ValueError as e:
                    pass  # e.g. insufficient cash
            elif signal['action'] == 'SELL':
                try:
                    self.portfolio.sell(self.ticker, quantity, current_price)
                except ValueError as e:
                    pass  # e.g. insufficient shares (SELL signal before any BUY)
            else:
                pass
            portfolio_value = self.portfolio.get_value(temp_df)
            self.results.append({
                'date': current_date,
                'portfolio_value': portfolio_value,
                'current_cash': self.portfolio.cash,
                'signal' : signal,
                'portfolio': self.portfolio.positions.copy()
            })
        return self.results

