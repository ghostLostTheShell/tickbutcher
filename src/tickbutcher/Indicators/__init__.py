from enum import Enum
from typing import Deque, Dict, Generic, Set, TypeVar
from tickbutcher.brokers.trading_pair import TradingPair
from tickbutcher.candlefeed import TimeframeType
from tickbutcher.candlefeed.candlefeed import CandleFeed
from tickbutcher.alphahub import AlphaHub

class DivergenceSignalState(Enum):
  NONE = 0
  BULLISH = 1   # 底背离
  BEARISH = -1  # 顶背离

V = TypeVar("V")
class PosValue(Generic[V]):
  """位置和值的组合"""
  position:int
  value:V

  def __init__(self, position:int, value:V):
    self.position = position
    self.value = value

R = TypeVar("R")

class Indicator(Generic[R], object):
  AlphaHub: 'AlphaHub'
  name:str
  result:Dict['TradingPair', Deque[R]]
  exclude_timeframes:Set[TimeframeType]

  def __init__(self, *, exclude_timeframes:Set[TimeframeType]=set()):
    self.result={}
    self.exclude_timeframes = exclude_timeframes

  def add_exclude_timeframe(self, timeframe: TimeframeType):
    self.exclude_timeframes.add(timeframe)

  def init(self):
    pass
  
  def set_alpha_hub(self, AlphaHub: 'AlphaHub'):
    self.AlphaHub = AlphaHub

  def get_result(self, trading_pair:'TradingPair'):
    value = self.result.get(trading_pair)
    if value is None:
      raise ValueError(f"获取交易对异常{trading_pair.id}")
    return value
  
  def get_curret_result(self, trading_pair:'TradingPair'):
    v = self.result.get(trading_pair)
    if v is None or len(v) == 0:
      return None
    return v[-1]
    
    
  def calculate(self, 
                *, 
                position:int,
                candle:CandleFeed, 
                timeframe: TimeframeType):
    ...

  
  def next(self):
    for candle in self.AlphaHub.candle_list:
      timeframe_level = candle.timeframe_level.value
      while True:
        if timeframe_level < 0 or timeframe_level < self.AlphaHub.timeframe_level.value :
          break
        timeframe = TimeframeType(timeframe_level)
        if timeframe not in self.exclude_timeframes:
          self.calculate(position=self.AlphaHub.current_time, 
                        candle=candle, 
                        timeframe=TimeframeType(timeframe_level))
          
        timeframe_level = timeframe_level-1


  def is_long_signal(self, trading_pair: TradingPair) -> bool:
    return False

  def is_short_signal(self, trading_pair: TradingPair) -> bool:
    return False