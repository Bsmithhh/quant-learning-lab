import yfinance as yf  # type: ignore



def fetch_prices(ticker, start, end):
    df = yf.download(ticker, start=start, end=end, progress=False)

    if df.empty:
        raise ValueError(f"No data returned for ticker: {ticker}")

    required_columns = {"Open", "High", "Low", "Close", "Adj Close", "Volume"}
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        raise ValueError(f"Missing columns: {missing}")

    df = df.sort_index()

    df["ret_1d"] = df["Adj Close"].pct_change()
    df = df.dropna(subset=["ret_1d"])
    price_cols = ["Open","High","Low","Close","Adj Close"]
    df[price_cols] = df[price_cols].ffill()
    df = df.dropna(subset=["Volume"])



    return df

fetch_prices("AAPL","2023-01-01", "2023-02-01")
