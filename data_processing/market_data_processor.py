import yfinance as yf
import pandas as pd

class MarketDataProcessor:
    def __init__(self, ticker: str, start: str, end: str):
        self.ticker = ticker
        self.start = start
        self.end = end
        self.data = None

    def fetch_prices(self):
        """
        Fetch and clean historical price data.

        Returns:
            pd.DataFrame: Cleaned OHLCV price data with forward-filled prices.
        """
        df = yf.download(self.ticker, start=self.start, end=self.end, progress=False)

        

        self.data = df.sort_index()

        price_cols = ["Open", "High", "Low", "Close", "Adj Close"]
        self.data[price_cols] = self.data[price_cols].ffill()
        self.data["Volume"] = self.data["Volume"].fillna(0)

        return self.data

    def add_returns(self):
        if self.data is None:
            raise RuntimeError("Call fetch_prices() first")

        self.data["ret_1d"] = self.data["Adj Close"].pct_change()
        self.data = self.data.dropna(subset=["ret_1d"])
        return self.data
    
    def validate(self):
        if self.data is None:
            raise RuntimeError("No data loaded. Call fetch_prices() first.")

        if self.data.empty:
            raise ValueError(f"No data returned for ticker: {self.ticker}")

        required_columns = {"Open", "High", "Low", "Close", "Adj Close", "Volume"}
        missing = required_columns - set(self.data.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        if not isinstance(self.data.index, pd.DatetimeIndex):
            raise ValueError("Index must be a pandas DatetimeIndex")

        if not self.data.index.is_monotonic_increasing:
            raise ValueError("Index is not sorted ascending")

        if self.data.index.has_duplicates:
            raise ValueError("Duplicate timestamps in index")
    def summary(self):
        """
        Return basic statistics for adjusted returns.
        """
        if self.data is None or "ret_1d" not in self.data.columns:
            raise RuntimeError("Returns not calculated yet")

        return {
            "mean_daily_return": self.data["ret_1d"].mean(),
            "volatility": self.data["ret_1d"].std(),
            "min_return": self.data["ret_1d"].min(),
            "max_return": self.data["ret_1d"].max(),
            "num_days": len(self.data)
        }

    def build(self):
        self.fetch_prices()
        self.add_returns()
        self.validate()
        return self.data
