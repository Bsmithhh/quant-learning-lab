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
        df = yf.download(self.ticker, start=self.start, end=self.end, progress=False, auto_adjust=False)

        # Flatten MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0).tolist()
        
        self.data = df.sort_index()

        price_cols = ["Open", "High", "Low", "Close", "Adj Close"]
        self.data[price_cols] = self.data[price_cols].ffill()
        self.data["Volume"] = self.data["Volume"].fillna(0)

        return self.data

    def add_returns(self, period: int = 1):
        """
        Compute daily returns from adjusted prices.
        Assumes data is time-ordered and adjusted for splits/dividends.
        """
        if self.data is None:
            raise RuntimeError("Call fetch_prices() first")

        col_name = f"ret_{period}d"
        self.data[col_name] = self.data["Adj Close"].pct_change(periods=period)
        self.data = self.data.dropna(subset=[col_name])
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
        if (self.data["Adj Close"] <= 0).any():
            raise ValueError("Invalid prices detected")

    def summary(self, period: int = 1):
        """
        Return basic statistics for adjusted returns.
        """
        if self.data is None:
            raise RuntimeError("No data loaded")
        col = f"ret_{period}d"
        if col not in self.data.columns:
            self.add_returns(period)
        return {
            "mean_daily_return": self.data[f"ret_{period}d"].mean(),
            "volatility": self.data[f"ret_{period}d"].std(),
            "min_return": self.data[f"ret_{period}d"].min(),
            "max_return": self.data[f"ret_{period}d"].max(),
            "num_days": len(self.data)
        }
    def diagnostics(self, period: int = 1):
        if self.data is None:
            raise RuntimeError("No data has been loaded")
        if self.data.empty:
            raise ValueError(f"No data returned for ticker: {self.ticker}")
        if  f"ret_{period}d" not in self.data.columns:
            raise ValueError("Missing returns column")
        num_rows: int = len(self.data)
        if num_rows == 0:
            raise ValueError("Dataframe is empty")
        start_date = self.data.index[0]
        end_date = self.data.index[-1]
        mean: float = self.data[f"ret_{period}d"].mean()
        standard_deviation: float = self.data[f"ret_{period}d"].std()
        max_return: float = self.data[f"ret_{period}d"].max()
        zero_vol_count: int = len(self.data[self.data['Volume'] == 0])
        percent_zero: float = (zero_vol_count/num_rows) * 100
        is_increasing: bool = self.data.index.is_monotonic_increasing
        is_index_unique: bool = self.data.index.is_unique
        return{
            'start_date' : start_date,
            'end_date': end_date,
            'mean' : mean,
            'standard_deviation': standard_deviation,
            'max_return' : max_return,
            "min_return": self.data[f"ret_{period}d"].min(),
            'zero_vol_count' : zero_vol_count,
            'percent_zero' : percent_zero,
            'is_increasing' : is_increasing,
            'is_index_unique': is_index_unique
        }

    def build(self):
        self.fetch_prices()
        self.validate()
        self.add_returns(1)
        stats = self.summary(1)
        return self.data, stats
