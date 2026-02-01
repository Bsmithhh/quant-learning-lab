# Strategy base class + implementations
import pandas as pd

class Strategy:
    def generate_signal(self):
        raise NotImplementedError("Subclasses must implement generate_signal()")

class MovingAverageCrossover:
    """
    Simple moving average crossover strategy.
    BUY when short MA crosses above long MA.
    SELL when short MA crosses below long MA.
    """

    def __init__(self,short_window = 20, long_window = 50, quantity = 100):
        self.short_window = short_window
        self.long_window = long_window
        self.quantity = quantity

    def generate_signal(self, data):
        if len(data) < self.long_window:
            return {'action': 'HOLD', 'quantity': 0}
        copy = data.copy()
        copy['ma_short'] = copy['close'].rolling(self.short_window).mean()
        copy['ma_long'] = copy['close'].rolling(self.long_window).mean()
        short_today = copy['ma_short'].iloc[-1]
        long_today = copy['ma_long'].iloc[-1]
        short_yesterday = copy['ma_short'].iloc[-2]
        long_yesterday = copy['ma_long'].iloc[-2]
        if short_yesterday <= long_yesterday and short_today > long_today:
            return {'action': 'BUY', 'quantity': self.quantity}
        if short_yesterday >= long_yesterday and short_today < long_today:
            return {'action': 'SELL', 'quantity': self.quantity}
        return {'action': 'HOLD', 'quantity': 0}

