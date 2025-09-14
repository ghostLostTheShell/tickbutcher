# type: ignore
from collections import deque

from collections import deque
from typing import Optional, Tuple, List


class MFIRealTime:
    def __init__(self, period: int = 14, lookback: int = 3):
        self.period = period
        self.lookback = lookback
        self.tp_window = deque(maxlen=period)
        self.pos_mf = deque(maxlen=period)
        self.neg_mf = deque(maxlen=period)

        # 保存历史 MFI 和价格用于背离检测
        self.mfi_history: List[float] = []
        self.price_history: List[float] = []

    def update(self, high: float, low: float, close: float, volume: float) -> Tuple[Optional[float], int, Optional[str]]:
        """
        更新一根新K线，返回 (MFI值, 信号强度, 背离信号)
        - MFI值: None 或 float
        - 信号强度: -2, -1, 0, 1, 2
        - 背离信号: "顶背离" / "底背离" / None
        """
        tp = (high + low + close) / 3.0
        mf = tp * volume

        if self.tp_window:
            tp_prev = self.tp_window[-1]
            if tp > tp_prev:
                self.pos_mf.append(mf)
                self.neg_mf.append(0.0)
            elif tp < tp_prev:
                self.pos_mf.append(0.0)
                self.neg_mf.append(mf)
            else:
                self.pos_mf.append(0.0)
                self.neg_mf.append(0.0)
        else:
            self.pos_mf.append(0.0)
            self.neg_mf.append(0.0)

        self.tp_window.append(tp)

        if len(self.tp_window) < self.period:
            return None, 0, None

        pos_sum = sum(self.pos_mf)
        neg_sum = sum(self.neg_mf)

        if neg_sum == 0 and pos_sum > 0:
            mfi = 100.0
        elif pos_sum == 0 and neg_sum > 0:
            mfi = 0.0
        elif pos_sum == 0 and neg_sum == 0:
            mfi = 50.0
        else:
            mr = pos_sum / neg_sum
            mfi = 100 - 100 / (1 + mr)

        # 保存历史数据
        self.mfi_history.append(mfi)
        self.price_history.append(close)

        # === 信号强弱 ===
        signal = 0
        if len(self.mfi_history) > 1:
            if mfi > self.mfi_history[-2]:
                if mfi > 80:
                    signal = 2  # 强烈多头
                else:
                    signal = 1
            elif mfi < self.mfi_history[-2]:
                if mfi < 20:
                    signal = -2  # 强烈空头
                else:
                    signal = -1

        # === 背离检测 ===
        divergence = self._detect_divergence()

        return mfi, signal, divergence

    def _detect_divergence(self) -> Optional[str]:
        """
        简单背离检测：找最近 lookback 范围的局部极值
        """
        if len(self.mfi_history) < self.lookback * 2:
            return None

        prices = self.price_history
        mfis = self.mfi_history
        i = len(prices) - 1  # 最新点

        # 顶背离：价格创新高但 MFI 没创新高
        if prices[i] > max(prices[i - self.lookback : i]) and mfis[i] < max(mfis[i - self.lookback : i]):
            return "顶背离"

        # 底背离：价格创新低但 MFI 没创新低
        if prices[i] < min(prices[i - self.lookback : i]) and mfis[i] > min(mfis[i - self.lookback : i]):
            return "底背离"

        return None


mfi_calc = MFIRealTime(period=5)

data = [
    (10, 9, 9.5, 100),
    (11,10,10.5,120),
    (12,11,11.5,150),
    (13,12,12.5,130),
    (12,11,11.8,160),
    (14,13,13.5,90),
    (14,13,13.5,90),
    (14,13,13.5,90),
    (14,13,13.5,90),
    (60,11,13.5,180),
]

for h,l,c,v in data:
    val = mfi_calc.update(h,l,c,v)
    print("MFI:", val)
