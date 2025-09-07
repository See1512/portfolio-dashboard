import pandas as pd

# List of required columns
REQUIRED_COLUMNS = {"date", "ticker", "side", "qty", "price"}

# Read trade data from a CSV file
def read_trades(file_path) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df.columns = [col.strip().lower() for col in df.columns]
    
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {', '.join(sorted(missing))}")
    
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
    df["fees"] = pd.to_numeric(df.get("fees", 0).fillna(0.0), errors="coerce")
    df["currency"] = df.get("currency", "EUR")

    return df[["date", "ticker", "side", "qty", "price", "fees", "currency"]]
