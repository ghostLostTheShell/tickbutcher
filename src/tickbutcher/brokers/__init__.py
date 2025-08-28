from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING, Dict, List, Optional
from tickbutcher.commission import Commission
from tickbutcher.order import Order, OrderType, OrderSide, OrderStatus
from tickbutcher.products import AssetType
from tickbutcher.trade import Trade
from tickbutcher.brokers.trading_pair import TradingPair

# 在运行时这个导入不会被执行，从而避免循环导入
if TYPE_CHECKING:
    from tickbutcher.contemplationer import Contemplationer

class OrderStatusEvent():
  order: Order
  event_type: OrderStatus

  def __init__(self, order: Order, event_type: OrderStatus):
    self.order = order
    self.event_type = event_type
    
class TradeStatusEvent():
  trade: Trade
  event_type: str

  def __init__(self, trade: Trade, event_type: str):
    self.trade = trade
    self.event_type = event_type

OrderStatusEventCallback = Callable[[OrderStatusEvent], None]

TradeStatusEventCallback = Callable[[TradeStatusEvent], None]

class Broker(ABC):

  @property
  @abstractmethod
  def asset_value()-> Dict[AssetType, float]:
      pass

  @abstractmethod
  def get_asset_value(self, asset_type: AssetType) -> float:
      pass

  @abstractmethod
  def submit_order(self, 
                   *,
                   symbol:str, 
                   type:OrderType,
                   side:OrderSide,
                   leverage:Optional[int]=None,
                   quantity:Optional[int]=None,
                   price:Optional[int]=None
                   ):
    """执行买入操作

    如果 OrderType 为市价单，则直接以当前市场价格下单
    如果 OrderType 为限价单，参数 price 不能为空
    """
    pass

  @abstractmethod
  def set_contemplationer(self, contemplationer: 'Contemplationer'):
    pass

  @abstractmethod
  def set_commission(self, trading_pair: TradingPair, commission: Commission):
    pass

  @abstractmethod
  def get_commission(self, trading_pair: TradingPair) -> Commission:
    pass
  
  @abstractmethod
  def next(self):
    pass
  
  @abstractmethod
  def trigger_order_changed_event(self, event: OrderStatusEvent):
    """
    触发定单事件
    """
    pass


  @abstractmethod
  def add_order_changed_event_listener(self, listener: OrderStatusEventCallback):
    """
    添加事件监听器
    """
    pass

  @abstractmethod
  def remove_order_changed_event_listener(self, listener: OrderStatusEventCallback):
    """
    移除事件监听器
    """
    pass

  @abstractmethod
  def trigger_trade_changed_event(self, event: OrderStatusEvent):
    """
    触发仓位事件
    """
    pass
  
  @abstractmethod
  def add_trade_changed_event_listener(self, listener: TradeStatusEventCallback):
    pass
  
  @abstractmethod
  def remove_trade_changed_event_listener(self, listener: TradeStatusEventCallback):
    pass

  @abstractmethod
  def get_order_list(self) -> List[Order]:
    pass

  @abstractmethod
  def get_trade_list(self) -> List[Trade]:
    pass