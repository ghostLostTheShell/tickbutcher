# type: ignore
from collections import deque

class MFIRealTime:
  def __init__(self, period=14): 
      self.period = period
      self.tp_window = deque(maxlen=period)
      self.pos_mf = deque(maxlen=period)
      self.neg_mf = deque(maxlen=period)

  def update(self, high, low, close, volume):
      """
      输入一根新K线，返回最新MFI值（数据不足时返回 None）
      """
      tp = (high + low + close) / 3.0
      mf = tp * volume

      if self.tp_window:  # 有前值
          tp_prev = self.tp_window[-1]
          if tp > tp_prev:
              self.pos_mf.append(mf)
              self.neg_mf.append(0.0)
          elif tp < tp_prev:
              self.pos_mf.append(0.0)
              self.neg_mf.append(mf)
          else:  # 相等
              self.pos_mf.append(0.0)
              self.neg_mf.append(0.0)
      else:  # 第一条数据
          self.pos_mf.append(0.0)
          self.neg_mf.append(0.0)

      self.tp_window.append(tp)

      # 数据不足
      if len(self.tp_window) < self.period:
          return None

      pos_sum = sum(self.pos_mf)
      neg_sum = sum(self.neg_mf)

      if neg_sum == 0 and pos_sum > 0:
          return 100.0
      elif pos_sum == 0 and neg_sum > 0:
          return 0.0
      elif pos_sum == 0 and neg_sum == 0:
          return 50.0
      else:
          mr = pos_sum / neg_sum
          return 100 - 100 / (1 + mr)

mfi_calc = MFIRealTime(period=5)

data = [
    (10, 9, 9.5, 100),
    (11,10,10.5,120),
    (12,11,11.5,150),
    (13,12,12.5,130),
    (12,11,11.8,160),
    (14,13,13.5,170),
]

for h,l,c,v in data:
    val = mfi_calc.update(h,l,c,v)
    print("MFI:", val)
