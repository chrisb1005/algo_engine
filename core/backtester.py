import pandas as pd
from core.indicators import compute_indicators
from core.signals import generate_signal
from core.strategies import decide_action

def backtest(df):
    df = compute_indicators(df)
    df.dropna(inplace=True)

    trades = []
    position = None

    for i in range(50, len(df)):
        window = df.iloc[:i]
        sig = generate_signal(window)
        action = decide_action(sig)
        price = df["Close"].iloc[i]

        if action in ("BUY_CALL", "BUY_PUT"):
            position = {"entry": price, "type": action}
        elif action == "NO_TRADE" and position:
            # exit position
            pnl = price - position["entry"] if "CALL" in position["type"] else position["entry"] - price
            trades.append(pnl)
            position = None

    return trades
