
from collections.abc import Callable
from typing import TYPE_CHECKING, Dict, List, Optional
from tickbutcher.commission import Commission
from tickbutcher.order import Order, OrderOptionType, OrderSide
from tickbutcher.products import AssetType
from tickbutcher.trade import Trade

if TYPE_CHECKING:
  from tickbutcher.contemplationer import Contemplationer
  from tickbutcher.brokers import Broker, BrokerEvent

class CommonBroker(Broker):
  contemplationer:'Contemplationer'
  commission_table:Dict[AssetType, Commission]
  order_changed_event_listener: List[Callable[[BrokerEvent], None]] = None
  trade_changed_event_listener: List[Callable[[BrokerEvent], None]] = None

  def __init__(self):
    self.commission_table = {}
    
  def set_contemplationer(self, contemplationer: 'Contemplationer'):
    self.contemplationer = contemplationer

  def set_commission(self, asset_type: AssetType, commission: Commission):
    self.commission_table[asset_type] = commission
  
  def get_commission(self, asset_type: AssetType) -> Commission:
    return self.commission_table.get(asset_type)
  
  def trigger_order_changed_event(self, event: 'BrokerEvent'):
    """
    触发事件
    """
    pass
  def trigger_trade_changed_event(self, event: 'BrokerEvent'):
    """
    触发事件
    """
    pass

  def add_order_changed_event_listener(self, listener):
    """
    添加事件监听器
    """
    pass

  def remove_trade_changed_event_listener(self,listener):
    """
    移除事件监听器
    """
    pass
  
  def get_order_list(self)->List[Order]:
    return []
  
  def get_trade_list(self)->List[Trade]:
    return []
  
  def next(self):
    pass
  
  def submit_order(self, 
                   *,
                   symbol:str, 
                   type:OrderOptionType,
                   side:OrderSide,
                   leverage:Optional[int]=None,
                   quantity:Optional[int]=None,
                   price:Optional[int]=None
                   ):
    pass