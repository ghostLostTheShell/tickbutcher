from abc import ABC, abstractmethod
import enum
from typing import TYPE_CHECKING, List, Optional
from tickbutcher.commission import Commission
from tickbutcher.order import Order, OrderOptionType, OrderSide
from tickbutcher.products import AssetType
from tickbutcher.trade import Trade

# 在运行时这个导入不会被执行，从而避免循环导入
if TYPE_CHECKING:
    from tickbutcher.contemplationer import Contemplationer

class BrokerEvent(enum.Enum):
  order_changed = 1
  trade_changed = 2

class Broker(ABC):
  
  @abstractmethod
  def submit_order(self, 
                   *,
                   symbol:str, 
                   type:OrderOptionType,
                   side:OrderSide,
                   leverage:Optional[int]=None,
                   quantity:Optional[int]=None,
                   price:Optional[int]=None
                   ):
    """执行买入操作

    如果 OrderOptionType 为市价单，则直接以当前市场价格下单
    如果 OrderOptionType 为限价单，参数 price 不能为空
    """
    pass

  @abstractmethod
  def set_contemplationer(self, contemplationer: 'Contemplationer'):
    pass

  @abstractmethod
  def set_commission(self, asset_type: AssetType, commission: Commission):
    pass
  
  @abstractmethod  
  def get_commission(self, asset_type: AssetType) -> Commission:
    pass
  
  @abstractmethod
  def next(self):
    pass
  
  @abstractmethod
  def trigger_order_changed_event(self, event: 'BrokerEvent'):
    """
    触发定单事件
    """
    pass
  @abstractmethod
  def trigger_trade_changed_event(self, event: 'BrokerEvent'):
    """
    触发仓位事件
    """
    pass

  @abstractmethod
  def add_order_changed_event_listener(self, listener):
    """
    添加事件监听器
    """
    pass

  @abstractmethod
  def remove_trade_changed_event_listener(self,listener):
    """
    移除事件监听器
    """
    pass
  
  @abstractmethod  
  def get_order_list(self)->List[Order]:
    pass
  
  @abstractmethod  
  def get_trade_list(self)->List[Trade]:
    pass