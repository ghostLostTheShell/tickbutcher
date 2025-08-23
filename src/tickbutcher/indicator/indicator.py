from pandas import DataFrame
import math
import random

class KData:
    def __init__(self, data: DataFrame):
        self.data = data
        self.open = data['open']
        self.high = data['high']
        self.low = data['low']
        self.close = data['close']
        self.date = data['date']

    def __getitem__(self, item):
        return self.data.iloc[item]

class indicator:
    def __init__(self, Kline: KData, index=0, period=5):
        # 确保 index 和 period 的 范围有效
        if len(Kline.data) < period:
            raise ValueError("Kline 数据长度不足以计算指定的周期")

        self.Kline = Kline
        self.index = index
        self.period = period

        # 根据 index 和 period 获取 open 数据
        open_values = [Kline.open[i].item() for i in range(index - 1, index - period - 1, -1)]
        self.open_values = open_values

        # 初始化其他属性
        self.high_values = [Kline.high[i].item() for i in range(index - 1, index - period - 1, -1)]
        self.low_values = [Kline.low[i].item() for i in range(index - 1, index - period - 1, -1)]
        self.close_values = [Kline.close[i].item() for i in range(index - 1, index - period - 1, -1)]

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

    def rsv(self,index=0):
        """仅计算当前点的 RSV 值"""
        low_min = min(self.low_values[index])
        high_max = max(self.high_values)
        current_close = self.close_values[-1] # 当前收盘价是切片中的最后一个
        if high_max == low_min:
            return 50.0
        return (current_close - low_min) / (high_max - low_min) * 100

    def kdj(self):
        """
        计算单点的 KDJ 值。
        这个方法必须依赖外部传入的前一日 K 和 D 值。
        """
        # 1. 计算当日 RSV
        current_rsv = self.rsv(index=-1)

      
        # 2. 计算当日 K 值
        k = (2* prev_k + current_rsv) / 3

        # 3. 计算当日 D 值
        d = (2* prev_d + k) / 3

        # 4. 计算当日 J 值
        j = 3 * k - 2 * d
        
        for i in range(5, len(Kline)):
         ind = indicator(Kline, index=i, period=5)
         k, d, j = ind.kdj(prev_k, prev_d)
         print(f"Index {i}: K={k}, D={d}, J={j}")
        # 更新 prev_k 和 prev_d
         prev_k, prev_d = k, d
         return k, d, j

    def RSI(self):
        """
        在 indicator 类内部计算指定 index 的 RSI 值。
        该方法使用 Wilder's Smoothing Method，这是最常见的 RSI 计算方式。
        它会从头迭代计算，以获取正确的历史平均值。
        """
        # 1. 检查计算的先决条件
        # RSI 需要 period+1 个数据点来计算 period 个价格变化
        if self.index < self.period:
            # 在周期完成前，RSI 是无定义的
            return None
        # 2. 提取需要的所有历史收盘价
        # 我们需要从 K线数据的开头一直到当前 index 的所有收盘价
        close_prices = [k.close for k in self.Kline[:self.index + 1]]
        # 3. 计算所有的价格变动（涨幅和跌幅）
        gains = []
        losses = []
        # 从第二个数据点开始，计算与前一点的差值
        for i in range(1, len(close_prices)):
            change = close_prices[i] - close_prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                # 损失记录为正数
                gains.append(0)
                losses.append(abs(change))
        # 确保 gains 和 losses 列表有足够的数据
        if len(gains) < self.period:
            return None
        # 4. 计算第一个周期的平均涨幅和平均跌幅 (使用简单移动平均)
        # 这只用于初始化
        initial_avg_gain = sum(gains[:self.period]) / self.period
        initial_avg_loss = sum(losses[:self.period]) / self.period
        # 5. 从第一个周期结束后开始，使用平滑法迭代计算
        # 直到我们到达目标 index
        avg_gain = initial_avg_gain
        avg_loss = initial_avg_loss
        # 注意：gains/losses 列表的索引比 close_prices 列表的索引小 1
        # 我们从第 period 个变化开始循环 (对应第 period+1 个收盘价)
        for i in range(self.period, len(gains)):
            avg_gain = (avg_gain * (self.period - 1) + gains[i]) / self.period
            avg_loss = (avg_loss * (self.period - 1) + losses[i]) / self.period
        # 6. 计算最终的 RSI 值
        if avg_loss == 0:
            # 如果平均跌幅为0，说明市场极度强势，RSI 为 100
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def BOLL(self, k=2):
        """
        计算布林带 (Bollinger Bands) 的上、中、下轨。
        参数:
        k (float): 标准差的倍数，通常为 2。
        返回:
        tuple: 包含 (上轨, 中轨, 下轨) 的元组。如果数据不足则返回 (None, None, None)。
        """
        # 1. 检查计算的先决条件
        # 计算 period 期的移动平均和标准差，至少需要 period 个数据点
        if self.index < self.period - 1:
            return None, None, None
        # 2. 获取当前周期内的所有收盘价
        start_index = self.index - self.period + 1
        close_prices = [d.close for d in self.Kline[start_index : self.index + 1]]
        # 3. 计算中轨 (MB) - 就是简单移动平均线 (SMA)
        middle_band = sum(close_prices) / self.period
        # 4. 计算标准差 (Standard Deviation)
        #   a. 计算每个价格点与均值的差的平方
        variance = sum([(price - middle_band) ** 2 for price in close_prices]) / self.period
        #   b. 取平方根得到标准差
        std_dev = math.sqrt(variance)
        # 5. 计算上轨 (UB) 和下轨 (LB)
        upper_band = middle_band + (k * std_dev)
        lower_band = middle_band - (k * std_dev)

        return upper_band, middle_band, lower_band