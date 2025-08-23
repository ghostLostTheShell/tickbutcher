from indicator import indicator, KData

# 初始化一个空的 Kline 列表

Kline = []
def main():
    ma = indicator.indicator(Kline, index=10, period=5).MA()
    ema = indicator.indicator(Kline, index=10, period=5).EMA()
    print(f"MA: {ma}, EMA: {ema}")
    pass