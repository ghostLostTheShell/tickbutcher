from datetime import datetime, timedelta, timezone as TimeZone
from typing import List, Optional
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
               timezone:TimeZone=None):
    self.trading_pair = trading_pair
    self.timeframe_level = timeframe_level
    
    if timezone is None:
      self.timezone_offset = 0
      self.timezone = TimeZone(timedelta(0))
    elif timezone is not None:
      offset = datetime.now(timezone).utcoffset()
      self.timezone_offset = offset.total_seconds() * 1000
      self.timezone = timezone
      
    self.timeframe_level = timeframe_level




  def get_position_index_list(self) -> List[any]:
    pass

  # 时间框架数据  
  def sec1(self):
    pass
  def min1(self, *, offset:Optional[int]=0):
    pass
  def min5(self):
    pass
  def min15(self):
    pass
  def h1(self):
    pass
  def h4(self):
    pass
  def d1(self):
    pass
  def w1(self):
    pass
  def mo1(self):
    pass
  def y1(self):
    pass

  