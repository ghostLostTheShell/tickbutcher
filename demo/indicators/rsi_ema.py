import pandas as pd
import numpy as np

def rsi_ema(series, period=14):
    """
    用 EMA 方式计算 RSI
    series: 收盘价序列 (pd.Series)
    period: 周期 (默认14)
    """
    delta = series.diff()

    # 涨跌分开
    U = delta.where(delta > 0, 0.0)
    D = -delta.where(delta < 0, 0.0)

    # 计算 EMA
    ema_u = U.ewm(span=period, adjust=False).mean()
    ema_d = D.ewm(span=period, adjust=False).mean()

    RS = ema_u / ema_d
    RSI = 100 - (100 / (1 + RS))

    return RSI

# ========== 示例 ==========
np.random.seed(42)
prices = np.cumsum(np.random.randn(100)) + 100  # 随机生成收盘价
close = pd.Series(prices)

rsi_values = rsi_ema(close, period=14)
print(rsi_values.tail())
