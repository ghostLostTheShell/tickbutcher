from tickbutcher.brokers import Broker
from tickbutcher.contemplationer import Contemplationer

class Strategy():
  
  def __init__(self, broker:Broker):
    self.broker = broker
  
  def next(self):
    self.candled


  @property
  def candled(self):
    return self


  def close_trade(self):
    self.broker.close_trade()

  def buy(self):
    self.broker.buy()
    
  def sell(self):
    self.broker.sell()
    
    