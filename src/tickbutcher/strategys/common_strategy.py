from tickbutcher.brokers import Broker
from tickbutcher.brokers.account import Account
from tickbutcher.brokers.common_broker import CommonBroker
from tickbutcher.brokers.trading_pair import TradingPair
from tickbutcher.order import OrderSide, OrderType, PosSide, TradingMode
from tickbutcher.products import AssetType
from tickbutcher.strategys import Strategy
from typing import Optional


class CommonStrategy(Strategy):

  broker:Broker
  account:Account
  
  
  def __init__(self):
    pass
    
  def init(self):
    self.broker = self.contemplationer.get_broker(CommonBroker)
    self.account = self.broker.register_account()
   
  def next(self):
    pass
    
  @property
  def candled(self):
    return self.contemplationer.candle


  def get_open_position(self, trading_pair: TradingPair, pos_side:PosSide, trading_mode:Optional[TradingMode]=None):
    if trading_mode is None:
      match trading_pair.base.type:
        case AssetType.PerpetualSwap:
          trading_mode = TradingMode.Isolated
        case _:
          trading_mode = TradingMode.Spot
          
    return self.account.get_open_position(trading_pair, pos_side=pos_side, trading_mode=trading_mode)

  # 交易相关的方法
  def long_entry(self, 
                 trading_pair: TradingPair, 
                 quantity:float,
                 *, 
                 order_type: OrderType, 
                 price:Optional[float]=None,
                 trading_mode: Optional[TradingMode]=None,
                 ):
    
    self.broker.submit_order(
      account=self.account,
      trading_pair=trading_pair,
      order_type=order_type,
      quantity=quantity,
      price=price,
      side=OrderSide.Buy,
      pos_side=PosSide.Long,
      trading_mode=trading_mode,
    )
  
  def long_close(self, 
                 trading_pair: TradingPair, 
                 quantity:float,
                 *, 
                 order_type: OrderType, 
                 price:Optional[float]=None,
                 trading_mode: Optional[TradingMode]=None,
                 ):
    pass

  def short_entry(self, 
                 trading_pair: TradingPair, 
                 quantity:float,
                 *, 
                 order_type: OrderType, 
                 price:Optional[float]=None,
                 trading_mode: Optional[TradingMode]=None,
                 ):
    pass

  def short_close(self, 
                 trading_pair: TradingPair, 
                 quantity:float,
                 *, 
                 order_type: OrderType, 
                 price:Optional[float]=None,
                 trading_mode: Optional[TradingMode]=None,
                 ):

    pass