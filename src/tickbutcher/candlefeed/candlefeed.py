from datetime import datetime, timedelta, timezone as TimeZone
from typing import Any, List, Optional, overload

from pandas import DataFrame, Series
from tickbutcher.brokers.trading_pair import TradingPair
from tickbutcher.candlefeed import TimeframeType

class CandleFeed():
  timezone:TimeZone
  trading_pair:TradingPair
  timeframe_level: TimeframeType
  timezone_offset:int
  
  def __init__(self, *, 
               trading_pair:TradingPair,
               timeframe_level:TimeframeType,
               timezone:Optional[TimeZone]=None):
    self.trading_pair = trading_pair
    self.timeframe_level = timeframe_level
    
    if timezone is None:
      self.timezone_offset = 0
      self.timezone = TimeZone(timedelta(0))
    else:
      offset = datetime.now(timezone).utcoffset()
      self.timezone_offset = int(offset.total_seconds() * 1000) # type: ignore
      self.timezone = timezone
      
    self.timeframe_level = timeframe_level




  def get_position_index_list(self) -> List[int]: # type: ignore
    pass

  @overload
  def get_ohlcv(self, position:int, *, timeframe:TimeframeType)-> Series[Any] :# type: ignore
    pass
  
  def get_ohlcv(self, position:int, *, timeframe:TimeframeType, length:int=1)-> DataFrame:# type: ignore
    pass
  # 时间框架数据  
  def sec1(self, position:int, *, offset:int=0, length:int=1)-> Series[Any] | DataFrame: # type: ignore
    ...
    
  def min1(self, position:int, *, offset:int=0, length:int=1):
    pass
  def min5(self, position:int, *, offset:int=0, length:int=1):
    pass
  def min15(self, position:int, *, offset:int=0, length:int=1):
    pass
  def h1(self, position:int, *, offset:int=0, length:int=1):
    pass
  def h4(self, position:int, *, offset:int=0, length:int=1):
    pass
  def d1(self, position:int, *, offset:int=0, length:int=1):
    pass
  def w1(self, position:int, *, offset:int=0, length:int=1):
    pass
  def mo1(self, position:int, *, offset:int=0, length:int=1):
    pass
  def y1(self, position:int, *, offset:int=0, length:int=1):
    pass

  