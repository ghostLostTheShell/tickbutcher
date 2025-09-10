from abc import ABC, abstractmethod
from tickbutcher.brokers import Broker
from tickbutcher.brokers.account import Account
from tickbutcher.brokers.trading_pair import TradingPair

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from tickbutcher.contemplationer import Contemplationer
class Strategy(ABC):
    
  @abstractmethod
  def next(self):
    pass

  @abstractmethod
  def set_broker(self, broker:Broker):
    pass
  
  def set_contemplationer(self, contemplationer: 'Contemplationer'):
    self.contemplationer = contemplationer

    

class CommonStrategy(Strategy):

  broker:Broker
  account:Account
  contemplationer: 'Contemplationer'
  
  def __init__(self):
    super().__init__()
    
  def set_contemplationer(self, contemplationer: 'Contemplationer'):
    self.contemplationer = contemplationer    
    
  def next(self):
    pass

  def set_broker(self, broker: Broker):
    self.broker = broker
  
  def set_account(self, account:Account):
    pass
    
  
  @property
  def candled(self):
    return self.contemplationer.candle

  def close_trade(self, trading_pair:TradingPair):
    print("平仓")

  def buy(self):
    pass
    # self.broker.submit_order(
    #   account=self.account,
    # )
    
  def sell(self):
    pass
    # self.broker.sell()