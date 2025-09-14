
from typing import TYPE_CHECKING, Dict, List, Optional
import uuid
from tickbutcher.brokers.account import Account
from tickbutcher.brokers.position import Position
from tickbutcher.brokers.trading_pair import TradingPair
from tickbutcher.commission import Commission, CommissionType, MakerTakerCommission
from tickbutcher.order import Order, OrderStatus, OrderType, OrderSide
from tickbutcher.brokers import Broker, OrderStatusEventCallback, PositionStatusEvent, OrderStatusEvent, PositionStatusEventCallback
from tickbutcher.products import AssetType

if TYPE_CHECKING:
  from tickbutcher.contemplationer import Contemplationer
  from tickbutcher.order import PosSide,TradingMode
class CommonBroker(Broker):
  contemplationer:'Contemplationer'
  order_changed_event_listener: List[OrderStatusEventCallback]
  position_changed_event_listener: List[PositionStatusEventCallback]
  order_list: List[Order]
  order_completed_list: List[Order]
  order_pending_list: List[Order]
  _accounts:List[Account]
  tradingPair_commission_map: Dict[TradingPair, Commission]
  name:str = "common_broker"

  def __init__(self):
    self.order_list = []
    self.order_completed_list = []
    self._accounts = []
    self.default_commission = MakerTakerCommission(8, 10)
    self.default_ps_commission = MakerTakerCommission(2, 5, c_type=CommissionType.MakerTakerOnQuote)
    self.order_changed_event_listener = []
    self.position_changed_event_listener = [] 
    self.order_pending_list = []
    
  def add_pending_order(self, order:Order):
    if order.status is not OrderStatus.Pending and order.status is not OrderStatus.PartiallyFilled:
      raise ValueError("只能添加状态为Pending或PartiallyFilled的订单")
    if order not in self.order_pending_list:
      self.order_pending_list.append(order)

  def remove_pending_order(self, order:Order):
    if order in self.order_pending_list:
      self.order_pending_list.remove(order)

  def set_commission(self, trading_pair: TradingPair, commission:Commission):
    self.tradingPair_commission_map[trading_pair] = commission
  
  def get_commission(self, trading_pair: TradingPair)->Commission:
    result = self.tradingPair_commission_map.get(trading_pair)
    if result is None:
      match trading_pair.base.type:
        case AssetType.PerpetualSwap:
          self.tradingPair_commission_map.setdefault(trading_pair, self.default_ps_commission)
          result = self.default_ps_commission
        case _:
          self.tradingPair_commission_map.setdefault(trading_pair, self.default_commission)
          result = self.default_commission
        
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
  def get_contemplationer(self) -> 'Contemplationer':
    return self.contemplationer

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
    for order in self.order_pending_list:
      order.account.process_order(order)
    
    
    # 清理已经完成的订单

  def submit_order(self, 
                   *,
                  account: 'Account',
                  trading_pair: TradingPair,
                  order_type: OrderType,
                  side: OrderSide,
                  quantity: float,
                  trading_mode:Optional[TradingMode]=None,
                  pos_side: Optional['PosSide']=None,
                  price: Optional[float] = None,
                  reduce_only:Optional[bool]=None
                   ) -> None:
    # 创建订单
    
    if trading_mode is None:
      match trading_pair.base.type:
        case AssetType.PerpetualSwap:
          trading_mode = TradingMode.Isolated
        case _:
          trading_mode = TradingMode.Spot
  

    order = Order(
      trading_mode=trading_mode,
      trading_pair=trading_pair,
      quantity=quantity,
      side=side,
      order_type=order_type,
      price=price,
      account=account,
      pos_side=pos_side,
      reduce_only=reduce_only,
    )
    
    order.status = OrderStatus.Created
    order.created_at = self.contemplationer.current_time
    order.set_id(self.generate_order_id())
    self.trigger_order_changed_event(OrderStatusEvent(order=order, event_type=OrderStatus.Created))
    
    self.order_list.append(order)
    order.account.process_order(order)
    
  
  def generate_order_id(self) -> int:
    """生成订单id"""
    if len(self.order_list) == 0:
      return 0
    else:
      return self.order_list[-1].id + 1

  def generate_position_id(self) -> int:
    """生成交易id"""
    u = uuid.uuid4()
    return u.int
    
    
  def generate_account_id(self) -> int:
    """生成账户id"""
    if len(self._accounts) == 0:
      return 0
    else:
      return self._accounts[-1].id + 1