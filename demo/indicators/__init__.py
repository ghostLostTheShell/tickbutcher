import pandas as pd

def macd(prices, short=12, long=26, signal=9):
    ema_short = prices.ewm(span=short, adjust=False).mean()
    ema_long = prices.ewm(span=long, adjust=False).mean()
    dif = ema_short - ema_long
    dea = dif.ewm(span=signal, adjust=False).mean()
    macd_hist = 2 * (dif - dea)
    return dif, dea, macd_hist

# 示例：收盘价序列
prices = pd.Series([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16])
dif, dea, hist = macd(prices)
print(dif, dea, hist)
