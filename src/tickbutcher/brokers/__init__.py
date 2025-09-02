from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING, List, Optional

from tickbutcher.order import PosSide

# 在运行时这个导入不会被执行，从而避免循环导入
if TYPE_CHECKING:
  from tickbutcher.contemplationer import Contemplationer
  from tickbutcher.brokers.account import Account
  from tickbutcher.brokers.position import Position
  from tickbutcher.order import Order, OrderType, OrderSide, OrderStatus,TradingMode
  from tickbutcher.commission import Commission
  from tickbutcher.brokers.trading_pair import TradingPair
  
class OrderStatusEvent():
  order: 'Order'
  event_type: 'OrderStatus'

  def __init__(self, order: 'Order', event_type: 'OrderStatus'):
    self.order = order
    self.event_type = event_type
    
class PositionStatusEvent():
  trade: 'Position'
  event_type: str

  def __init__(self, trade: 'Position', event_type: str):
    self.trade = trade
    self.event_type = event_type

OrderStatusEventCallback = Callable[[OrderStatusEvent], None]

PositionStatusEventCallback = Callable[[PositionStatusEvent], None]

class Broker(ABC):

  @abstractmethod
  def register_account(self) -> 'Account':
      pass

  @property
  @abstractmethod
  def accounts(self)-> List['Account']:
      pass


  @abstractmethod
  def submit_order(self, 
                   *,
                  account: 'Account',
                  trading_pair: 'TradingPair',
                  order_type: 'OrderType',
                  side: 'OrderSide',
                  trading_mode: 'TradingMode',
                  quantity: float,
                  pos_side: Optional['PosSide']=None,
                  price: Optional[int] = None,
                  reduce_only:Optional[bool]=None
                  ) -> None:
    """
    
    
    
    如果 OrderType 为市价单，则直接以当前市场价格下单
    如果 OrderType 为限价单，参数 price 不能为空
    """
    pass

  @abstractmethod
  def set_contemplationer(self, contemplationer: 'Contemplationer'):
    pass

  @abstractmethod
  def set_commission(self, trading_pair: 'TradingPair', commission: 'Commission'):
    pass

  @abstractmethod
  def get_commission(self, trading_pair: 'TradingPair') -> 'Commission':
    pass
  
  @abstractmethod
  def next(self):
    pass
  
  @abstractmethod
  def trigger_order_changed_event(self, event: 'OrderStatusEvent'):
    """
    触发定单事件
    """
    pass


  @abstractmethod
  def add_order_changed_event_listener(self, listener: 'OrderStatusEventCallback'):
    """
    添加事件监听器
    """
    pass

  @abstractmethod
  def remove_order_changed_event_listener(self, listener: 'OrderStatusEventCallback'):
    """
    移除事件监听器
    """
    pass

  @abstractmethod
  def trigger_position_changed_event(self, event: 'PositionStatusEvent'):
    """
    触发仓位事件
    """
    pass
  
  @abstractmethod
  def add_position_changed_event_listener(self, listener: 'PositionStatusEventCallback'):
    pass
  
  @abstractmethod
  def remove_position_changed_event_listener(self, listener: 'PositionStatusEventCallback'):
    pass

  @abstractmethod
  def get_order_list(self, account: 'Account', 
                     *, 
                     trading_pairs: Optional[List['TradingPair']]=None,
                     ) -> List['Order']:
    pass

  @abstractmethod
  def get_position_list(self, 
                        account: 'Account', 
                        *, 
                        trading_pairs: Optional[List['TradingPair']]=None, # 过滤交易对
                        ) -> List['Position']:
    pass