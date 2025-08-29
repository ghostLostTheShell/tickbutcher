
from typing import TYPE_CHECKING, Dict, List, Optional, overload
from tickbutcher.brokers.account import Account
from tickbutcher.brokers.position import Position
from tickbutcher.brokers.trading_pair import TradingPair
from tickbutcher.commission import Commission, MakerTakerCommission
from tickbutcher.order import Order, OrderStatus, OrderType, OrderSide
from tickbutcher.brokers import Broker, OrderStatusEventCallback, PositionStatusEvent, OrderStatusEvent, PositionStatusEventCallback
from tickbutcher.products import AssetType

if TYPE_CHECKING:
  from tickbutcher.contemplationer import Contemplationer

class CommonBroker(Broker):
  contemplationer:'Contemplationer'
  order_changed_event_listener: List[OrderStatusEventCallback]
  position_changed_event_listener: List[PositionStatusEventCallback]
  order_list: List[Order]
  order_completed_list: List[Order]
  position_list: List[Position]
  _accounts:List[Account]
  tradingPair_commission_map: Dict[TradingPair, Commission]

  def __init__(self):
    self.order_list = []
    self.order_completed_list = []
    self.position_list = []
    self._accounts = []
    self.default_commission = MakerTakerCommission(0.02, 0.05)
    self.order_changed_event_listener = []
    self.position_changed_event_listener = [] 

  def set_commission(self, trading_pair: TradingPair, commission:Commission):
    self.tradingPair_commission_map[trading_pair] = commission
  
  def get_commission(self, trading_pair: TradingPair)->Commission:
    result = self.tradingPair_commission_map.get(trading_pair)
    if result is None:
      return self.tradingPair_commission_map.setdefault(trading_pair, self.default_commission)
        
    return result

  @property
  def accounts(self):
    return self._accounts
  
  def register_account(self):
    account_id = self.generate_account_id()
    account = Account(id=account_id, broker=self)
    self._accounts.append(account)
    return account
    
  def set_contemplationer(self, contemplationer: 'Contemplationer'):
    self.contemplationer = contemplationer


  def trigger_order_changed_event(self, event: OrderStatusEvent):
    """
    触发事件
    """
    for listener in self.order_changed_event_listener:
      listener(event) 

  def add_order_changed_event_listener(self, listener: OrderStatusEventCallback):
    """
    添加事件监听器
    """
    self.order_changed_event_listener.append(listener)


  def remove_order_changed_event_listener(self, listener: OrderStatusEventCallback):
    """
    移除事件监听器
    """
    self.order_changed_event_listener.remove(listener)


  def trigger_position_changed_event(self, event: PositionStatusEvent):
    """
    触发事件
    """
    for listener in self.position_changed_event_listener:
      listener(event)

  def add_position_changed_event_listener(self, listener: PositionStatusEventCallback):
    """
    添加事件监听器
    """
    self.position_changed_event_listener.append(listener)

  def remove_position_changed_event_listener(self, listener: PositionStatusEventCallback):
    """
    移除事件监听器
    """
    self.position_changed_event_listener.remove(listener)
    
    

  def get_order_list(self, account: Account, 
                     *, 
                     trading_pairs: Optional[List[TradingPair]]=None,
                     ) -> List[Order]:
    
    
    return []

  def get_position_list(self, 
                        account: Account, 
                        *, 
                        trading_pairs: Optional[List[TradingPair]]=None, # 过滤交易对
                        ) -> List[Position]:
    return []
  
  def next(self):
    pass
  
  


  
  def handle_market_order(self, order: Order):
    trading_pair = order.trading_pair
    account =order.account
    
    current = self.contemplationer.candle[0, order.trading_pair.id]
    order.execution_price = current.close
    order.execution_quantity = order.quantity
    # 创建仓位
    position = Position(account=account, trading_pair=trading_pair, quantity=order.execution_quantity)
    self.position_list.append(position)

    # 设置asset_value_list
    match trading_pair.base.type:
      case AssetType.PerpetualSwap:
        pass
      
      case _:
        order.asset_value_list = [current.close * order.quantity]


      
      
  @overload
  def submit_order(self,
                  *,
                  trading_pair: TradingPair,
                  order_type: OrderType,
                  side: OrderSide,
                  quantity: Optional[int] = None,
                  price: Optional[int] = None,
                  ):
    ...  
  def submit_order(self, *args, **kwargs):
    # 创建订单
    
    order = Order(**kwargs)
    order.status = OrderStatus.Created
    order.created_at = self.contemplationer.current_time
    self.trigger_order_changed_event(OrderStatusEvent(order=order, event_type=OrderStatus.Created))
    self.order_list.append(order)
    
    

    if order.order_type is OrderType.MarketOrder:
      # 市价立即成交
      self.handle_market_order(order)
      
    elif order.order_type is OrderType.StopOrder:
      #止损单
      self.handle_stop_order(order)

    else:
      raise ValueError(f"不支持的订单类型: {order.order_type}")

  
  def generate_order_id(self) -> int:
    """生成订单id"""
    if len(self.order_list) == 0:
      return 0
    else:
      return self.order_list[-1] + 1

  def generate_position_id(self) -> int:
    """生成交易id"""
    if len(self.position_list) == 0:
      return 0
    else:
      return self.position_list[-1] + 1
    
    
  def generate_account_id(self) -> int:
    """生成账户id"""
    if len(self._accounts) == 0:
      return 0
    else:
      return self._accounts[-1] + 1