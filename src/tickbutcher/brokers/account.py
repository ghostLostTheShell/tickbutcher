
from typing import Dict, List, TYPE_CHECKING


# 在运行时这个导入不会被执行，从而避免循环导入
if TYPE_CHECKING:
  from tickbutcher.brokers import Broker
  from tickbutcher.brokers.position import Position
  from tickbutcher.brokers.trading_pair import TradingPair
  from tickbutcher.order import Order
  from tickbutcher.brokers.margin import MarginType
  from tickbutcher.products import AssetType

class Account(object):
  id: int
  default_leverage:int
  asset_value_map: Dict['AssetType', float]
  trading_pair_leverage:Dict['TradingPair', int]
  trading_pair_margin_type: Dict['TradingPair', 'MarginType']
  order_list: List['Order']
  position_list: List['Position']
  broker: 'Broker' # 所属的经纪商

  def __init__(self, *, id: int, broker:'Broker'):
    self.id = id
    self.asset_value_map = {}
    self.trading_pair_leverage = {}
    self.default_leverage = 1
    self.order_list = []
    self.position_list = []
    self.broker = broker

  def add_order(self, order: 'Order'):
    self.order_list.append(order)

  def set_margin_type(self, margin_type: 'MarginType', trading_pair: 'TradingPair'):
    self.trading_pair_margin_type[trading_pair] = margin_type

  def get_margin_type(self, trading_pair: 'TradingPair') -> 'MarginType':
    if trading_pair not in self.trading_pair_margin_type:
      self.trading_pair_margin_type[trading_pair] = 'MarginType.Isolated'

    return self.trading_pair_margin_type.get(trading_pair)
  

  def set_leverage(self, leverage: float, trading_pair: 'TradingPair'):
    self.trading_pair_leverage[trading_pair] = leverage

  def get_leverage(self, trading_pair: 'TradingPair') -> int:
    if trading_pair not in self.trading_pair_leverage:
      self.trading_pair_leverage[trading_pair] = self.default_leverage
      
    return self.trading_pair_leverage.get(trading_pair)  

  def deposit(self, asset_type: 'AssetType', amount: float):
    """
    存款
    """
    self.asset_value_map[asset_type] = self.asset_value_map.get(asset_type, 0) + amount

  def withdraw(self, asset_type: 'AssetType', amount: float):
    """
    取款
    """
    self.asset_value_map[asset_type] = self.asset_value_map.get(asset_type, 0) - amount
