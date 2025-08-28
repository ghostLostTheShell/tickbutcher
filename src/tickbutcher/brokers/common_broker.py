
from typing import TYPE_CHECKING, Dict, List, Optional
from tickbutcher.commission import Commission
from tickbutcher.order import Order, OrderStatus, OrderType, OrderSide
from tickbutcher.products import AssetType, FinancialInstrument
from tickbutcher.trade import Trade, TradeStatus
from tickbutcher.brokers import Broker, OrderStatusEventCallback, TradeStatusEventCallback, OrderStatusEvent, TradeStatusEvent

if TYPE_CHECKING:
  from tickbutcher.contemplationer import Contemplationer

class CommonBroker(Broker):
  contemplationer:'Contemplationer'
  commission_table:Dict[AssetType, Commission]
  order_changed_event_listener: List[OrderStatusEventCallback] = None
  trade_changed_event_listener: List[TradeStatusEventCallback] = None
  order_list: List[Order] = None
  order_completed_list: List[Order] = None
  trade_list: List[Trade] = None
  asset_value_list: Dict[AssetType, float] = None

  def __init__(self):
    self.commission_table = {}
    self.order_list = []
    self.order_completed_list = []
    self.trade_list = []

    
  def set_contemplationer(self, contemplationer: 'Contemplationer'):
    self.contemplationer = contemplationer

  def set_commission(self, asset_type: AssetType, commission: Commission):
    self.commission_table[asset_type] = commission
  
  def get_commission(self, asset_type: AssetType) -> Commission:
    return self.commission_table.get(asset_type)

  def trigger_order_changed_event(self, event: OrderStatusEvent):
    """
    触发事件
    """
    for listener in self.order_changed_event_listener:
      listener(event) 

  def trigger_trade_changed_event(self, event: TradeStatusEvent):
    """
    触发事件
    """
    for listener in self.order_changed_event_listener:
      listener(event)

  def trigger_trade_changed_event(self, event: TradeStatusEvent):
    """
    触发事件
    """
    for listener in self.trade_changed_event_listener:
      listener(event)

  def add_order_changed_event_listener(self, listener):
    """
    添加事件监听器
    """
    self.order_changed_event_listener.append(listener)

  def remove_trade_changed_event_listener(self,listener):
    """
    移除事件监听器
    """
    self.order_changed_event_listener.remove(listener)

  def get_order_list(self)->List[Order]:
    return []
  
  def get_trade_list(self)->List[Trade]:
    return []
  
  def next(self):
    pass
  
  def deal_order(self, order: Order):
    """处理订单"""
    pass
  
  def submit_order(self, 
                   *,
                   financial_type:FinancialInstrument, 
                   order_option_type:OrderType,
                   side:OrderSide,
                   leverage:Optional[int]=None,
                   quantity:Optional[int]=None,
                   price:Optional[int]=None,
                   trade:Optional[Trade]=None):
    
    if order_option_type is OrderType.MarketOrder:
      current = self.contemplationer.candle[0, financial_type.id]
      #立即成交
      order = Order(financial_type=financial_type,
                    type=order_option_type,
                    side=side,
                    leverage=leverage,
                    quantity=quantity,
                    price=None,
                    id=self.generate_order_id())

      order.status = OrderStatus.Created
      self.trigger_order_changed_event(OrderStatusEvent(order=order, event_type=OrderStatus.Created))
      order.status = OrderStatus.Completed
      order.execution_price = current.close
      order.add_execution_quantity(current.volume)
      self.trigger_order_changed_event(OrderStatusEvent(order=order, event_type=OrderStatus.Completed))
      self.order_completed_list.append(order)
      
      trade = Trade(id=self.generate_trade_id(),
                    financial_type=financial_type)
      self.trade_list.append(trade)
      trade.add_order(order)
      self.trigger_trade_changed_event(TradeStatusEvent(trade=trade, event_type=TradeStatus.Open))


    if order_option_type is OrderType.LimitOrder:
      #限价单
      order = Order(financial_type=financial_type,
                    type=order_option_type,
                    side=side,
                    leverage=leverage,
                    quantity=quantity,
                    price=price,
                    
                    id=self.generate_order_id())
      
      self.trigger_order_changed_event(OrderStatusEvent(order=order, event_type=OrderStatus.Created))
      self.order_list.append(order)
      self.trigger_order_changed_event(OrderStatusEvent(order=order, event_type=OrderStatus.Submitted))


  
  def generate_order_id(self) -> int:
    """生成订单id"""
    if len(self.order_list) == 0:
      return 0
    else:
      return self.order_list[-1] + 1
    
  def generate_trade_id(self) -> int:
    """生成交易id"""
    if len(self.trade_list) == 0:
      return 0
    else:
      return self.trade_list[-1] + 1