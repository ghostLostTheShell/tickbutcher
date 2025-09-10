from typing import Deque, Dict, Generic, Set, TypeVar
from tickbutcher.brokers.trading_pair import TradingPair
from tickbutcher.candlefeed import TimeframeType
from tickbutcher.candlefeed.candlefeed import CandleFeed
from tickbutcher.contemplationer import Contemplationer

R = TypeVar("R")

class Indicator(Generic[R], object):
  contemplationer: 'Contemplationer'
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
  
  def set_contemplationer(self, contemplationer: 'Contemplationer'):
    self.contemplationer = contemplationer

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
    for candle in self.contemplationer.candle_list:
      timeframe_level = candle.timeframe_level.value
      while True:
        if timeframe_level < 0 or timeframe_level < self.contemplationer.timeframe_level.value :
          break
        timeframe = TimeframeType(timeframe_level)
        if timeframe not in self.exclude_timeframes:
          self.calculate(position=self.contemplationer.current_time, 
                        candle=candle, 
                        timeframe=TimeframeType(timeframe_level))
          
        timeframe_level = timeframe_level-1


