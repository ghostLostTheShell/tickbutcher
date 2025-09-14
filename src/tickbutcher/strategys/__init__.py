from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional
from tickbutcher.brokers.trading_pair import TradingPair
from tickbutcher.order import OrderType, TradingMode

if TYPE_CHECKING:
  from tickbutcher.contemplationer import Contemplationer
class Strategy(ABC):
  contemplationer: 'Contemplationer'
  
  @abstractmethod
  def next(self): ...
  
  def set_contemplationer(self, contemplationer: 'Contemplationer'):
    self.contemplationer = contemplationer

  @abstractmethod
  def init(self): ...
  # 交易相关的方法
  @abstractmethod
  def long_entry(self, 
                 trading_pair: TradingPair, 
                 quantity:float,
                 *, 
                 order_type: OrderType, 
                 price:Optional[float]=None,
                 trading_mode: Optional[TradingMode]=None): ...
  
  @abstractmethod
  def long_close(self, 
                 trading_pair: TradingPair, 
                 quantity:float,
                 *, 
                 order_type: OrderType, 
                 price:Optional[float]=None,
                 trading_mode: Optional[TradingMode]=None): ...

  @abstractmethod
  def short_entry(self, 
                 trading_pair: TradingPair, 
                 quantity:float,
                 *, 
                 order_type: OrderType, 
                 price:Optional[float]=None,
                 trading_mode: Optional[TradingMode]=None): ...
  
  @abstractmethod
  def short_close(self, 
                 trading_pair: TradingPair, 
                 quantity:float,
                 *, 
                 order_type: OrderType, 
                 price:Optional[float]=None,
                 trading_mode: Optional[TradingMode]=None): ...

