import numpy as np, pandas as pd
from math import sqrt

# Reconstruct the position of each trade
def reconstruct_pos(trades: pd.DataFrame) -> pd.DataFrame:
    t = trades.copy()
    t["signed_qty"] = np.where(t["side"].str.upper()=="BUY", t["qty"], -t["qty"])
    
    # Calculate daily shares per ticker
    pos = t.groupby(["ticker", "date"], as_index=False)["signed_qty"].sum().pivot(index="date", columns="ticker", values="signed_qty").fillna(0).sort_index().cumsum()
    return pos

# Calculate total portfolio market value
def portfolio_value(pos: pd.DataFrame, prices: pd.DataFrame) -> pd.Series:
    px = (prices
          .reindex(index=pos.index)
          .reindex(columns=pos.columns)
          .ffill())
    
    # Return value per ticker (shares x price)
    return (px * pos).sum(axis=1)

# Calculate time-weighted return
def twr(values: pd.Series) -> float:
    daily_returns = values.pct_change().dropna()
    return float((1 + daily_returns).prod() - 1)

# Calculate annualized volatility
def annualized_volatility(values: pd.Series) -> float:
    daily_returns = values.pct_change().dropna()
    return float(daily_returns.std() * sqrt(252))

# Calculate maximum drawdown
def max_drawdown(values: pd.Series) -> float:
    rolling_max = values.cummax()
    drawdowns = (values - rolling_max) / rolling_max
    return float(drawdowns.min())