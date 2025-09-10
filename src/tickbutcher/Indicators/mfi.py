"""
MFI(资金流量指标,Money Flow Index)
"""

from collections import deque
from typing import TYPE_CHECKING, Deque, Dict
from tickbutcher.Indicators import Indicator
from tickbutcher.candlefeed import TimeframeType
from tickbutcher.candlefeed.candlefeed import CandleFeed

if TYPE_CHECKING:
  from tickbutcher.brokers.trading_pair import TradingPair
  
class MoneyFlowIndex(Indicator[float]):
  name:str = 'mfi'
  _tp_window:Dict['TradingPair', Deque[float]]
  _pos_mf:Dict['TradingPair', Deque[float]]
  _neg_mf:Dict['TradingPair', Deque[float]]
  period:int
  # result:Dict['TradingPair', Deque[float]]
  
  def __init__(self, *, period:int=14):
    super().__init__()
    self._tp_window = {}
    self._pos_mf = {}
    self._neg_mf = {}
    self.period = period
    
  
  def init(self):
    for candle in self.contemplationer.candle_list:
      self._tp_window[candle.trading_pair] = deque(maxlen=self.period)
      self._pos_mf[candle.trading_pair] = deque(maxlen=self.period)
      self._neg_mf[candle.trading_pair] = deque(maxlen=self.period)
      self.result[candle.trading_pair] = deque(maxlen=self.period)
  
  def get_tp_window(self, trading_pair:'TradingPair'):
    value = self._tp_window.get(trading_pair)
    if value is None:
      raise ValueError(f"获取交易对异常{trading_pair.id}")
    return value
  
  def get_pos_mf(self, trading_pair:'TradingPair'):
    value = self._pos_mf.get(trading_pair)
    if value is None:
      raise ValueError(f"获取交易对异常{trading_pair.id}")
    return value
  
  def get_neg_mf(self, trading_pair:'TradingPair'):
    value = self._neg_mf.get(trading_pair)
    if value is None:
      raise ValueError(f"获取交易对异常{trading_pair.id}")
    return value  
    
  def get_result(self, trading_pair:'TradingPair'):
    value = self.result.get(trading_pair)
    if value is None:
      raise ValueError(f"获取交易对异常{trading_pair.id}")
    return value     
  
  def calculate(self,
                *,
                position:int,
                candle:CandleFeed, 
                timeframe: TimeframeType):
    series = candle.get_ohlcv(position, timeframe=timeframe)
    trading_pair = candle.trading_pair
    

    tp = (series.high + series.low + series.close) / 3.0
    mf = tp * series.volume
    
    tp_window = self.get_tp_window(trading_pair)
    pos_mf = self.get_pos_mf(trading_pair)
    neg_mf = self.get_neg_mf(trading_pair)
    
    if tp_window:  # 有前值
        tp_prev = tp_window[-1]
        if tp > tp_prev:
            pos_mf.append(mf)
            neg_mf.append(0.0)
        elif tp < tp_prev:
            pos_mf.append(0.0)
            neg_mf.append(mf)
        else:  # 相等
            pos_mf.append(0.0)
            neg_mf.append(0.0)
    else:  # 第一条数据
        pos_mf.append(0.0)
        neg_mf.append(0.0)

    tp_window.append(tp)

    # 数据不足
    if len(tp_window) < self.period:
        return None

    pos_sum = sum(pos_mf)
    neg_sum = sum(neg_mf)

    value:float = 0.0 
    if neg_sum == 0 and pos_sum > 0:
        value = 100.0
    elif pos_sum == 0 and neg_sum > 0:
        value = 0.0
    elif pos_sum == 0 and neg_sum == 0:
        value =  50.0
    else:
        mr = pos_sum / neg_sum
        value = 100 - 100 / (1 + mr)  

    result=self.get_result(trading_pair)
    result.append(value)
