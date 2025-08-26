
import enum
from typing import Dict, List, Optional, Tuple

from pandas import Series

from tickbutcher.products import FinancialInstrument


class TimeframeType(enum.Enum):
  s1 = 0
  min1 = 1
  min5 = 2
  min15 = 3
  h1 = 4
  h4 = 5
  d1 = 6
  w1 = 7
  mo1 = 8
  y1 = 9

from .candlefeed import CandleFeed

__all__ = ['CandleFeed', 'TimeframeType']

class CandleIndexer:
    position: int
    candleFeed: CandleFeed
    timeframe: TimeframeType
    financial_type_candle_table: Dict[FinancialInstrument, CandleFeed]

    def __init__(self, position: int, table: Dict[FinancialInstrument, CandleFeed]):
      self.position = position
      self.financial_type_candle_table = table
      self.timeframe = None
        
    def __getattr__(self, name: str):
      # bct_m15[-1]
      financial_type_id, timeframe = name.split("_")
      
      try:
        timeframe = TimeframeType[timeframe]
      except KeyError:
        raise ValueError(f"Invalid timeframe: {timeframe}")
      
      
      
      self.timeframe = TimeframeType[timeframe]
      
      for financial_type in self.financial_type_candle_table.keys():
        if financial_type.id == financial_type_id:
          self.candlefeed = self.financial_type_candle_table[financial_type]
          
      return self

    def __getitem__(self, key: Tuple[int , Optional[str]])->Series:

      row_indexer, candlefeed_indexer = key
      if candlefeed_indexer is not None:
        getattr(self, candlefeed_indexer)
      
      
      if self.candlefeed is None:
        raise ValueError("No candle feed available")


      else:
        
        
        if row_indexer == 0:
          return  getattr(self.candlefeed, self.timeframe.name)(self.position)

        elif row_indexer > 0:
          raise IndexError("Index out of range")
        else:
          return  getattr(self.candlefeed, self.timeframe.name)(self.position, offset=row_indexer)
          

