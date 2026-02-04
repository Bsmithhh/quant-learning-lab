# Portfolio class goes here


class Portfolio:
    def __init__(self, initial_cash: float = 100000):
        self.initial_cash = initial_cash
        self.positions: dict = {}
        self.trades: list = []
        self.cash = initial_cash

    def buy(self,ticker:str,quantity:int, price:float):
        cost = quantity * price
        if self.cash < cost:
            raise ValueError('Not enough cash to make this purchase.')
        self.cash = self.cash - cost
        self.positions[ticker] = self.positions.get(ticker, 0) + quantity
        self.trades.append({
            'ticker': ticker,
            'action': 'BUY',
            'quantity': quantity,
            'price': price,
            'cost': cost
        })
    
    def sell(self, ticker:str, quantity:int, price:float):
        current_position = self.positions.get(ticker, 0)
        if current_position < quantity:
            raise ValueError(f"Insufficient shares: trying to sell {quantity}, only have {current_position}")
        gain = quantity * price
        self.cash = self.cash + gain
        self.positions[ticker] = current_position - quantity
        self.trades.append({
            'ticker': ticker,
            'action': 'SELL',
            'quantity': quantity,
            'price': price,
            'gain': gain
        })

    def get_value(self, df):
        """
        Calculate portfolio value.
        
        Args:
            df: DataFrame with 'ticker' and 'close' columns
        """
        closes = df.groupby('ticker')['close'].last()
        total = self.cash
        for ticker, shares in self.positions.items():
            if ticker in closes:
                total += shares * closes[ticker]
            else:
                raise ValueError(f"No price data for {ticker}")
        return total



