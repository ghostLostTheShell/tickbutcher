
import enum
from typing import Dict, List, Optional, Tuple

from pandas import Series

from tickbutcher.brokers.trading_pair import TradingPair


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
      """
      动态解析属性名以获取特定交易对和时间周期的K线数据。

      通过属性名格式 '<financial_type_id>_<timeframe>' 或 '<financial_type_id>'，
      可以访问指定交易对和时间周期的K线数据。当只提供交易对ID时，默认使用最小时间周期。

      参数:
        name (str): 属性名，格式为 '<financial_type_id>_<timeframe>' 或 '<financial_type_id>'。

      返回:
        self: 返回自身实例，并更新 `timeframe` 和 `candlefeed` 属性。

      异常:
        ValueError: 当时间周期无效、交易对ID不存在或未找到对应K线数据时抛出。
      """
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

      tp = TradingPair.get_trading_pair(financial_type_id)
      self.candlefeed = self.trading_pair_candle_table[tp]
      if self.candlefeed is None:
        raise ValueError(f"No candle feed available for trading pair id: {financial_type_id}")  

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