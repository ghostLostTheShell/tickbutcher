from datetime import datetime
from zoneinfo import ZoneInfo
from tickbutcher.brokers.trading_pair import TradingPair
from tickbutcher.candlefeed import CandleFeed, CandleIndexer, TimeframeType
from tickbutcher.log import logger
from typing import Callable, Dict, List, TYPE_CHECKING, Type, TypeVar, ParamSpec, Any, cast


if TYPE_CHECKING:
  from tickbutcher.brokers import Broker
  from tickbutcher.strategys import Strategy
  from tickbutcher.Indicators import Indicator
  
  S = TypeVar("S", bound='Strategy')
  I = TypeVar("I", bound='Indicator[Any]')
  P = ParamSpec("P")
  B = TypeVar("B", bound='Broker')

class Contemplationer:
  brokers: 'List[Broker]'
  brokers_map: 'Dict[Type[Broker], Broker]'
  strategys: List['Strategy']
  candle_list: List[CandleFeed]
  trading_pair_candle_table: Dict[TradingPair, CandleFeed]
  indicators:List['Indicator[Any]']
  indicators_map:Dict[str, 'Indicator[Any]']
  current_time: int
  timeframe_level:TimeframeType

  def __init__(self, *, timeframe_level:TimeframeType, brokers:List['Broker']):
    self.timeframe_level = timeframe_level
    self.strategys = []
    self.candle_list = []
    self.trading_pair_candle_table = {}
    self.brokers = brokers
    self.indicators=[]
    self.indicators_map = {}
    for broker in brokers:
      broker.set_contemplationer(self)

  def add_broker(self, broker:'Callable[P, Broker]', *args:'P.args', **kwargs:'P.kwargs'):
    new_broker = broker(*args, **kwargs)
    new_broker.set_contemplationer(self)
    self.brokers.append(new_broker)

  def get_broker(self, index: 'Type[B]') -> 'B':
    b = self.brokers_map.get(index)
    if b is None:
      raise ValueError(f"Broker not found for type {index}")

    return cast('B', b)

  def set_current_time(self, current_time: int):
    self.current_time = current_time

  def add_indicator(self, indicator:'Callable[P, Indicator[Any]]', *args:'P.args', **kwargs:'P.kwargs') -> None:
    new_indicator = indicator(*args, **kwargs)
    new_indicator.set_contemplationer(self)
    new_indicator.init()
    self.indicators.append(new_indicator)
    self.indicators_map[new_indicator.name] = new_indicator
    

  def add_strategy(self, strategy:'Callable[P, S]', *args:'P.args', **kwargs:'P.kwargs') -> None:
    new_strategy = strategy(*args, **kwargs)
    new_strategy.set_contemplationer(self)
    self.strategys.append(new_strategy)

  def add_kline(self, *, candleFeed:CandleFeed):
    if candleFeed.timeframe_level != self.timeframe_level:
      raise ValueError(f"CandleFeed timeframe {candleFeed.timeframe_level} does not match Contemplationer timeframe {self.timeframe_level}")
    self.candle_list.append(candleFeed)
    self.trading_pair_candle_table[candleFeed.trading_pair] = candleFeed

  def get_time_interval(self):
    if len(self.candle_list) == 0:
      raise ValueError("No candle feed available")
    return self.candle_list[0].get_position_index_list()

  def run(self):
    time_interval = self.get_time_interval()
    
    for current_time in time_interval:
      self.set_current_time(current_time)
      
      for candle_feed in self.trading_pair_candle_table.values():
        candle_feed.update(current_time)

      for indicator in self.indicators:
        indicator.next()
      
      for broker in self.brokers:
        broker.next()

      for strategy in self.strategys:
        strategy.next()

      logger.debug(f"Current time: {datetime.fromtimestamp(current_time/1000, tz=ZoneInfo('UTC'))}")

  @property
  def candle(self):
    return CandleIndexer(self.current_time, self.trading_pair_candle_table, self.timeframe_level)
  
  def get_indicator(self, name: str, typ: 'Type[I]') -> 'I':
    return cast('I', self.indicators_map[name])