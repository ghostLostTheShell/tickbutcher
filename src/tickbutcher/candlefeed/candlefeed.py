from datetime import datetime, timedelta, timezone as TimeZone
from typing import List, Literal, Optional, overload

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
  def get_ohlcv(self, position:int, *, timeframe: TimeframeType) -> Series: ...
  
  @overload
  def get_ohlcv(self, position:int, *, timeframe: TimeframeType, offset:int, length: Literal[1] = 1) -> Series: ...
  
  @overload
  def get_ohlcv(self, position:int, *, timeframe: TimeframeType, offset:int, length: int) -> DataFrame: ...

  def get_ohlcv(self, position:int, *, timeframe:TimeframeType, offset:int=0, length:int=1)-> DataFrame | Series: ...

  # 时间框架数据  
  def sec1(self, position:int, *, offset:int=0, length:int=1)-> Series|DataFrame:
    ...
    
  def min1(self, position:int, *, offset:int=0, length:int=1)-> Series|DataFrame:
    ...
  def min5(self, position:int, *, offset:int=0, length:int=1)-> Series|DataFrame:
    ...
  def min15(self, position:int, *, offset:int=0, length:int=1)-> Series|DataFrame:
    ...
  def h1(self, position:int, *, offset:int=0, length:int=1)-> Series|DataFrame:
    ...
  def h4(self, position:int, *, offset:int=0, length:int=1)-> Series|DataFrame:
    ...
  def d1(self, position:int, *, offset:int=0, length:int=1)-> Series|DataFrame:
    ...
  def w1(self, position:int, *, offset:int=0, length:int=1)-> Series|DataFrame:
    ...
  def mo1(self, position:int, *, offset:int=0, length:int=1)-> Series|DataFrame:
    ...
  def y1(self, position:int, *, offset:int=0, length:int=1)-> Series|DataFrame:
    ...

  