import pandas as pd
import numpy as np

def compute_indicators(df):
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()

    # RSI
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # Simple momentum
    df["Momentum"] = df["Close"].pct_change(5)

    # Volatility
    df["Volatility"] = df["Close"].pct_change().rolling(10).std() * 100

    return df
