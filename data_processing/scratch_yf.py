import yfinance as yf  # type: ignore



def fetch_prices(ticker,start,end):
    df = yf.download(ticker,start=start,end = end, progress = False)
    df = df.sort_index()
    required_columns = {"Open","High","Low","Close","Adj Close","Volume"}
    df["ret_1d"] = df["Adj Close"].pct_change()
    df = df.iloc[1:]
    if required_columns.issubset(df.columns):
        if df.empty:
            raise ValueError(f"No data returned for ticker: {ticker}")
        print(df.index)
        print(df.index.is_monotonic_increasing)
        return df
    else:
       raise ValueError("One of more columns are missing")
fetch_prices("AAPL","2023-01-01", "2023-02-01")
