from indicator import indicator, KData

# 初始化一个空的 Kline 列表

Kline = []
def main():
    ma = indicator.indicator(Kline, index=30, period=5).MA()
    ema = indicator.indicator(Kline, index=30, period=5).EMA()  

    macd_calculator = indicator(Kline, index=30, period=12)
    print(f"MA: {ma}, EMA: {ema}")
    pass