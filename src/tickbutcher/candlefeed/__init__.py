
import enum
from typing import Dict, List, Optional, Tuple

from pandas import Series

from tickbutcher.brokers.trading_pair import TradingPair
from tickbutcher.products import FinancialInstrument


class TimeframeType(enum.Enum):
  sec1 = 0
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


class CandleIndexer:
    position: int
    candleFeed: CandleFeed
    timeframe: TimeframeType
    trading_pair_candle_table: Dict[TradingPair, CandleFeed]
    min_time_frame: TimeframeType

    def __init__(self, position: int, table: Dict[TradingPair, CandleFeed], min_time_frame: TimeframeType):
      self.position = position
      self.trading_pair_candle_table = table
      self.timeframe = None
      self.min_time_frame = min_time_frame


    def __getattr__(self, name: str):
      # bct_m15[-1]
      financial_type_id = "" 
      timeframe = ""
      
      ss = name.split("_")
      if len(ss) == 2:
        financial_type_id, timeframe = ss
      else:
        financial_type_id = ss[0]
        timeframe = self.min_time_frame.name

      try:
        self.timeframe = TimeframeType[timeframe]
      except KeyError:
        raise ValueError(f"Invalid timeframe: {timeframe}")


      for trading_pair in self.trading_pair_candle_table.keys():
        if trading_pair.id == financial_type_id:
          self.candlefeed = self.trading_pair_candle_table[trading_pair]

      return self

    def __getitem__(self, key: Tuple[int , Optional[str]])->Series:

      if not isinstance(key, tuple):
        row_indexer = key
        candlefeed_indexer = None
      else:
        row_indexer = key[0]
        candlefeed_indexer = key[1] if len(key) > 1 else None 
      
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
          

__all__ = ['CandleFeed', 'TimeframeType', 'CandleIndexer']