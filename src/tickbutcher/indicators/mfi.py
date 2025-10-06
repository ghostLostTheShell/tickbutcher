"""
MFI(资金流量指标,Money Flow Index)
"""

from collections import deque
from collections.abc import Callable
from typing import TYPE_CHECKING, Deque, Dict, Literal
from tickbutcher.indicators import DivergenceSignalState, Indicator, PosValue
from tickbutcher.candlefeed import TimeframeType
from tickbutcher.candlefeed.candlefeed import CandleFeed

if TYPE_CHECKING:
  from tickbutcher.brokers.trading_pair import TradingPair

class MFIResult(PosValue[float]):
  signal_strength:float
  divergence_signal:DivergenceSignalState

  def __init__(self, 
               position:int, 
               value:float, 
               signal_strength:float, 
               divergence_signal:DivergenceSignalState,):
    super().__init__(position=position, value=value)
    self.signal_strength = signal_strength
    self.divergence_signal = divergence_signal

class MoneyFlowIndex(Indicator[MFIResult]):
  name:str = 'mfi'
  _tp_window:Dict['TradingPair', Dict[TimeframeType,Deque[PosValue[float]]]]
  _pos_mf:Dict['TradingPair', Dict[TimeframeType,Deque[PosValue[float]]]]
  _neg_mf:Dict['TradingPair', Dict[TimeframeType,Deque[PosValue[float]]]]
  period:int
  result_maxlen:int
  trend_strength_handle: Callable[['TradingPair', TimeframeType], float]
  
  def __init__(self, *, 
                period:int=14, 
                result_maxlen:int=50,
                exclude_timeframes:set[TimeframeType]=set(),
                trend_strength_mode:Literal['instant', 'avg']= 'avg'):
    super().__init__(exclude_timeframes=exclude_timeframes)
    self._tp_window = {}
    self._pos_mf = {}
    self._neg_mf = {}
    self.period = period
    self.result_maxlen = result_maxlen

    match trend_strength_mode:
      case 'avg':
        self.trend_strength_handle = self._trend_strength_avg
      case 'instant':
        raise NotImplementedError("即时趋势强度计算未实现")

  def init(self):
    for candle in self.AlphaHub.candle_list:
      self._tp_window[candle.trading_pair] = {}
      self._pos_mf[candle.trading_pair] = {} 
      self._neg_mf[candle.trading_pair] = {}
      self.result[candle.trading_pair] = {}

      for timeframe in TimeframeType:
        if timeframe in self.exclude_timeframes:
          continue
        
        self._tp_window[candle.trading_pair][timeframe] = deque(maxlen=self.period)
        self._pos_mf[candle.trading_pair][timeframe] = deque(maxlen=self.period)
        self._neg_mf[candle.trading_pair][timeframe] = deque(maxlen=self.period)
        self.result[candle.trading_pair][timeframe] = deque(maxlen=self.result_maxlen)
  
  def get_tp_window(self, trading_pair:'TradingPair', timeframe: TimeframeType):
    value = self._tp_window.get(trading_pair, {}).get(timeframe)
    if value is None:
      raise ValueError(f"获取交易对异常{trading_pair.id}")
    return value
  
  def get_pos_mf(self, trading_pair:'TradingPair', timeframe: TimeframeType):
    value = self._pos_mf.get(trading_pair, {}).get(timeframe)
    if value is None:
      raise ValueError(f"获取交易对异常{trading_pair.id}")
    return value
  
  def get_neg_mf(self, trading_pair:'TradingPair', timeframe: TimeframeType):
    value = self._neg_mf.get(trading_pair, {}).get(timeframe)
    if value is None:
      raise ValueError(f"获取交易对异常{trading_pair.id}")
    return value

  def get_result(self, trading_pair:'TradingPair', timeframe: TimeframeType):
    value = self.result.get(trading_pair, {}).get(timeframe)
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
    high = series.high
    low = series.low
    close = series.close
    volume = series.volume
    series_p:int = series.name # type: ignore

    tp = (high + low + close) / 3.0
    mf = tp * volume

    tp_window = self.get_tp_window(trading_pair, timeframe)
    pos_mf = self.get_pos_mf(trading_pair, timeframe)
    neg_mf = self.get_neg_mf(trading_pair, timeframe)
    
    if tp_window:  # 有前值
        tp_prev = tp_window[-1]
        if tp > tp_prev:
            pos_mf.append(PosValue(position=series_p, value=mf))
            neg_mf.append(PosValue(position=series_p, value=0.0))
        elif tp < tp_prev:
            pos_mf.append(PosValue(position=series_p, value=0.0))
            neg_mf.append(PosValue(position=series_p, value=mf))
        else:  # 相等
            pos_mf.append(PosValue(position=series_p, value=0.0))
            neg_mf.append(PosValue(position=series_p, value=0.0))
    else:  # 第一条数据
        pos_mf.append(PosValue(position=series_p, value=0.0))
        neg_mf.append(PosValue(position=series_p, value=0.0))

    tp_window.append(tp)

    # 数据不足
    if len(tp_window) < self.period:
        return None

    pos_sum = sum(pos.value for pos in pos_mf)
    neg_sum = sum(neg.value for neg in neg_mf)

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

    result=self.get_result(trading_pair, timeframe)

    divergence_signal = self.detect_divergence(trading_pair, timeframe)

    mfi_result = MFIResult(
        position=series_p,
        value=value,
        signal_strength=0,
        divergence_signal=divergence_signal
    )

    if len(result) == 0 or result[-1].position != series_p:
        result.append(mfi_result)
    else:
        result[-1] = mfi_result

    mfi_result.signal_strength = self.trend_strength_handle(trading_pair, timeframe)


  def _trend_strength_avg(self, trading_pair: 'TradingPair', timeframe: TimeframeType) -> float:
    result = self.get_result(trading_pair, timeframe=timeframe)
    if not result:
        return 0.0
    avg = sum(i.value for i in result) / len(result)
    # 归一化到 [-1, 1] 区间
    norm = (avg - 50) / 30
    return round(norm, 2)

  def detect_divergence(self, trading_pair: 'TradingPair', timeframe: TimeframeType) -> DivergenceSignalState:
    """
    简单背离检测：找最近 lookback 范围的局部极值
    """
    result=self.get_result(trading_pair, timeframe)
    # lookback = 
    if len(result) < self.period:
        return DivergenceSignalState.NONE

    # prices = self.price_history
    # mfis = self.mfi_history
    # i = len(prices) - 1  # 最新点

    # # 顶背离：价格创新高但 MFI 没创新高
    # if prices[i] > max(prices[i - self.lookback : i]) and mfis[i] < max(mfis[i - self.lookback : i]):
    #     return "顶背离"

    # # 底背离：价格创新低但 MFI 没创新低
    # if prices[i] < min(prices[i - self.lookback : i]) and mfis[i] > min(mfis[i - self.lookback : i]):
    #     return "底背离"
    
    return DivergenceSignalState.NONE
  
__ALL__ = ['MoneyFlowIndex', 'MFIResult']