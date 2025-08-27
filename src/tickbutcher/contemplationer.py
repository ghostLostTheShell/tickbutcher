from datetime import datetime
from zoneinfo import ZoneInfo

from tickbutcher.candlefeed import CandleFeed, CandleIndexer, TimeframeType
from tickbutcher.log import logger
from tickbutcher.products import FinancialInstrument
from typing import Dict, List, TYPE_CHECKING, Type, TypeVar, ParamSpec
# 避免循环导入
if TYPE_CHECKING:
  from tickbutcher.brokers import Broker
  from tickbutcher.strategys import Strategy

P = ParamSpec("P")
T = TypeVar("T", bound='Strategy')
  

class Contemplationer:
  broker:'Broker'
  strategys: List['Strategy']
  candle_list: List[CandleFeed]
  financial_type_candle_table: Dict[FinancialInstrument, CandleFeed]
  current_time: int
  timeframe_level:TimeframeType
  
  def __init__(self, *, timeframe_level:TimeframeType):
    self.timeframe_level = timeframe_level
    self.strategys = []
    self.candle_list = []
    self.financial_type_candle_table = {}

  def set_broker(self, broker: 'Broker'):
    self.broker = broker
    broker.set_contemplationer(self)

  def set_current_time(self, current_time: int):
    self.current_time = current_time

  def add_strategy(self, strategy:Type['Strategy'], *args:P.args, **kwargs:P.kwargs) -> None:
    new_strategy = strategy(*args, **kwargs)
    self.strategys.append(new_strategy)

  def add_kline(self, *, candleFeed:CandleFeed):
    if candleFeed.timeframe_level != self.timeframe_level:
      raise ValueError(f"CandleFeed timeframe {candleFeed.timeframe_level} does not match Contemplationer timeframe {self.timeframe_level}")
    self.candle_list.append(candleFeed)
    self.financial_type_candle_table[candleFeed.financial_type] = candleFeed

  def get_time_interval(self):
    if len(self.candle_list) == 0:
      raise ValueError("No candle feed available")
    return self.candle_list[0].get_position_index_list()

  def run(self):
    time_interval = self.get_time_interval()
    
    if self.broker is None:
      raise ValueError("No broker set for contemplationer")
    else:
      for strategy in self.strategys:
        strategy.set_broker(self.broker)

    for current_time in time_interval:
      self.set_current_time(current_time)
      self.broker.next()
      
      for strategy in self.strategys:
        strategy.next()

      logger.debug(f"Current time: {datetime.fromtimestamp(current_time/1000, tz=ZoneInfo('UTC'))}")

  @property
  def candle(self):
    return CandleIndexer(self.current_time, self.financial_type_candle_table, self.timeframe_level)