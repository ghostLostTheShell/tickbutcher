from tickbutcher.brokers import Broker
from tickbutcher.contemplationer import Contemplationer

class Strategy():
  
  def __init__(self, broker:Broker, contemplationer:Contemplationer):
    self.broker = broker
    self.contemplationer = contemplationer
  
  def next(self):
    pass


  def data(self):
    return self.contemplationer.candle_feed_proxy

  def close_trade(self):
    self.broker.close_trade()

  def buy(self):
    self.broker.buy()
    
  def sell(self):
    self.broker.sell()
    
    