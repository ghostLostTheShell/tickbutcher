from abc import ABC, abstractmethod
from datetime import timezone as TimeZone
from typing import List, Optional, Set, TypeVar

from pandas import Series
from tickbutcher.brokers.trading_pair import TradingPair
from tickbutcher.candlefeed import TimeframeType

default_disable_timeframe: Set[TimeframeType] = set()
for t in TimeframeType:
    default_disable_timeframe.add(t)


C = TypeVar('C', bound='CandleFeed')

class CandleFeed(ABC):
  timezone:TimeZone
  trading_pair:TradingPair
  timeframe_level: TimeframeType
  timezone_offset:int
  disable_timeframe:Set[TimeframeType]

  def __init__(self, *, 
               trading_pair:TradingPair,
               timeframe_level:TimeframeType,
               timezone:Optional[TimeZone]=None,
               disable_timeframe:Optional[Set[TimeframeType]]=None):
    self.trading_pair = trading_pair
    self.timeframe_level = timeframe_level
    self.disable_timeframe = disable_timeframe or default_disable_timeframe

    if timezone is None:
      self.timezone_offset = 0
      self.timezone = TimeZone.utc
    else:
      self.timezone_offset = int(timezone.utcoffset(None).total_seconds()) # type: ignore
      self.timezone = timezone
      
    self.timeframe_level = timeframe_level

  # def enable_timeframe(self:C, timeframe:TimeframeType)->C:
  #   self.disable_timeframe.remove(timeframe)
  #   return self

  @abstractmethod
  def get_position_index_list(self) -> List[int]: ...


  @abstractmethod
  def get_ohlcv(self, position:int, *, timeframe:TimeframeType, offset:int=0) -> Series: ...
  
  @abstractmethod
  def update(self, position:int): ...