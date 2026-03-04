def decide_action(sig):
    rsi = sig["rsi"]
    trend = sig["trend"]

    # Buy Calls
    if trend == "Bullish" and 40 < rsi < 65:
        return "BUY_CALL"

    # Buy Puts
    if trend == "Bearish" and 35 < rsi < 70:
        return "BUY_PUT"

    # Sell Put / Sell Call
    if rsi < 30:
        return "SELL_PUT"
    if rsi > 70:
        return "SELL_CALL"

    return "NO_TRADE"
