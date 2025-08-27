from abc import ABC, abstractmethod
from tickbutcher.brokers import Broker

class Strategy(ABC):
    
  @abstractmethod
  def next(self):
    pass

  @abstractmethod
  def set_broker(self, broker:Broker):
    pass


    

class CommonStrategy(Strategy):

  broker:Broker
  
  def next(self):
    pass

  def set_broker(self, broker: Broker):
    self.broker = broker
    
  
  @property
  def candled(self):
    return self.broker.contemplationer.candle

  def close_trade(self):
    self.broker.close_trade()

  def buy(self):
    self.broker.buy()
    
  def sell(self):
    self.broker.sell()