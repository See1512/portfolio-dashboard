import pandas as pd, yfinance as yf
from functools import lru_cache

# Define cache for historical price data
@lru_cache(maxsize=256)
def get_prices(ticker: str, start:  str, end: str) -> pd.Series:
    df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    if df.empty:
        raise ValueError(f"No data found for {ticker} from {start} to {end}")
    close = df["Close"]

    # If multiple columns (e.g., multi-index), take the first
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close.name = ticker
    return close

# Get the price of a stock on a specific date
def get_price_on_date(tickers, start, end) -> pd.DataFrame:
    prices = [get_prices(t, start, end) for t in tickers]
    panel = pd.concat(prices, axis=1)
    panel = panel.loc[:, panel.notna().any()]
    return panel
