from datetime import datetime
from zoneinfo import ZoneInfo

from tickbutcher.candlefeed import CandleFeed
from tickbutcher.products import FinancialInstrument
from typing import Dict, List, TYPE_CHECKING
# 避免循环导入
if TYPE_CHECKING:
  from tickbutcher.brokers import Broker
  from tickbutcher.strategys import Strategy
class Contemplationer:
  broker:'Broker'
  strategys: List['Strategy']
  candle_list: List[CandleFeed]
  financial_type_candle__tble: Dict[FinancialInstrument, CandleFeed]
  current_time: int

  def __init__(self):
    self.strategys = []
    self.candle_list = []
    self.financial_type_candle__tble = {}

  def set_broker(self, broker: 'Broker'):
    self.broker = broker
    broker.set_contemplationer(self)

  def set_current_time(self, current_time: int):
    self.current_time = current_time

  def add_kline(self, *, candleFeed:CandleFeed):
    self.candle_list.append(candleFeed)
    self.financial_type_candle__tble[candleFeed.financial_type] = candleFeed

  def get_time_interval(self):
    if len(self.candle_list) == 0:
      raise ValueError("No candle feed available")
    return self.candle_list[0].get_position_index_list()

  def run(self):
    time_interval = self.get_time_interval()

    for current_time in time_interval:
      self.set_current_time(current_time)
      self.broker.next()
      
      for strategy in self.strategys:
        strategy.next()

      print(f"Current time: {datetime.fromtimestamp(current_time/1000, tz=ZoneInfo('UTC'))}")
