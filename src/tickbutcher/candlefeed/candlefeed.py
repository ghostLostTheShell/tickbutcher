from typing import List
from zoneinfo import ZoneInfo
from tickbutcher.candlefeed import TimeframeType
from tickbutcher.products import FinancialInstrument

class CandleFeed():
  timezone:ZoneInfo
  financial_type:FinancialInstrument
  timeframe_level: TimeframeType

  def __init__(self, *, 
               financial_type:FinancialInstrument,
               timeframe_level:TimeframeType,
               timezone:ZoneInfo=None):
    self.financial_type = financial_type
    self.timeframe_level = timeframe_level
    self.timezone = timezone or ZoneInfo("UTC")
    self.timeframe_level = timeframe_level




  def get_position_index_list(self) -> List[any]:
    pass

  # 时间框架数据  
  def s1(self):
    pass
  def min1(self, *, calc_enable=False):
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

  