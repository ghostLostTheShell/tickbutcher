from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional
from tickbutcher.brokers.trading_pair import TradingPair
from tickbutcher.order import OrderType, TradingMode

if TYPE_CHECKING:
  from tickbutcher.alphahub import AlphaHub
class Strategy(ABC):
  alpha_hub: 'AlphaHub'
  
  @abstractmethod
  def next(self): ...
  
  def set_alpha_hub(self, alpha_hub: 'AlphaHub'):
    self.alpha_hub = alpha_hub

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
                 *, 
                 order_type: OrderType,
                 quantity:Optional[float]=None,
                 price:Optional[float]=None,
                 trading_mode: Optional[TradingMode]=None,): ...

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

