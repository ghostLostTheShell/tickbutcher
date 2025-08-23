class Data:
    def __init__(self, open=0, high=0, low=0, close=0):
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.date = None

# 初始化一个空的 Kline 列表
Kline = []

class indicator:
    def __init__(self, Kline, index=0, period=5):
        # 确保 index 和 period 的 范围有效
        if len(Kline) < period:
            raise ValueError("Kline 数据长度不足以计算指定的周期")

        self.Kline = Kline
        self.index = index
        self.period = period

        # 根据 index 和 period 获取 open 数据
        open_values = [Kline[i].open for i in range(index, index - period, -1)]
        self.open_values = open_values

        # 初始化其他属性
        self.high_values = [Kline[i].high for i in range(index, index - period, -1)]
        self.low_values = [Kline[i].low for i in range(index, index - period, -1)]
        self.close_values = [Kline[i].close for i in range(index, index - period, -1)]

    def MA(self):
        # 计算简单移动平均线
        if len(self.close_values) < self.period:
            raise ValueError("数据长度不足以计算指定的周期")
        return sum(self.close_values[:self.period]) / self.period

    def EMA(self):
        # 计算指数移动平均线
        if len(self.close_values) < self.period:
            raise ValueError("数据长度不足以计算指定的周期")
        ema = [sum(self.close_values[:self.period]) / self.period]
        multiplier = 2 / (self.period + 1)
        for price in self.close_values[self.period:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])
        return ema[-1]
    
    def Fvg(self):
        # 计算某种指标（示例）
        return max(self.high_values) - min(self.low_values)



kdj
rsi
bollinger
macd
fvg
dol
亚欧美盘

