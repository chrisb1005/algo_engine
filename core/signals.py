def generate_signal(df):
    sig = {}
    sig["trend"] = "Bullish" if df["Close"].iloc[-1] > df["MA20"].iloc[-1] else "Bearish"
    sig["rsi"] = df["RSI"].iloc[-1]
    sig["vol"] = df["Volatility"].iloc[-1]
    sig["momentum"] = df["Momentum"].iloc[-1]
    return sig
