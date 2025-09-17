
import enum
from typing import TYPE_CHECKING

from tickbutcher.order import *

# 在运行时这个导入不会被执行，从而避免循环导入
if TYPE_CHECKING:
  from tickbutcher.brokers.trading_pair import TradingPair
class PositionStatus(enum.Enum):
  Active = 0  #持仓中
  Closed = 1  #已平仓
  ForcedLiq = 2  #强制平仓（ForcedLiquidation）

class SettlementRecord():
  pass


class Position(object):
  """仓位信息 仓位信息是指在Broker处理完毕订单数据后返回仓位信息"""
  id: int
  trading_pair: 'TradingPair' #用于记录合约期货类产品是用哪个交易对的
  status: PositionStatus
  orders: list['Order']  # 该仓位下的所有订单
  buy_orders: list['Order']  # 该仓位下的所有买入订单
  sell_orders: list['Order']  # 该仓位下的所有卖出订单
  amount: float  # 仓位数量/大小
  entry_price: float  # 开仓均价/持仓均价
  mark_price: float  # 标记价格
  realized_pnl: float  # 已实现盈亏
  leverage: float  # 杠杆倍数
  liq_price: float  # 强平价格/爆仓价(liquidation_price)
  pos_side: 'PosSide'  # 持仓方向，LONG (多头), SHORT (空头), 或 单方向仓
  trading_mode: 'TradingMode'  # 交易模式，逐仓或全仓,现金
  ps_funding: float  # 永续合约的资金费用
  total_cost: float  # 总成本
  account: 'Account'  # 该仓位所属的账户

  def __init__(self, 
               id: int,
               *,
               account: 'Account',
               leverage: int=1,
               trading_pair: 'TradingPair',
               pos_side: 'PosSide',
               trading_mode: 'TradingMode',
               ):
    self.leverage = leverage
    self.trading_pair = trading_pair
    self.id = id
    self.orders = []
    self.status = PositionStatus.Active
    self.pos_side = pos_side
    self.trading_mode = trading_mode
    self.amount = 0.0
    self.entry_price = 0.0
    self.mark_price = 0.0
    self.buy_orders = []
    self.sell_orders = []
    self.account = account

  def add_order(self, order: 'Order'):
    #计算持仓均价
    if order not in self.orders:
      self.orders.append(order)
      match order.side:
        case OrderSide.Buy:
          self.buy_orders.append(order)
        case OrderSide.Sell:
          self.sell_orders.append(order)
          
    self.calculate_transact_status()

  def is_active(self):
    return self.status is PositionStatus.Active

  def is_closed(self):
    return self.status in (PositionStatus.Closed, PositionStatus.ForcedLiq)

  def unrealized_pnl(self, current_price: float) -> float:
    """计算未实现盈亏"""
    if self.pos_side == PosSide.Long:
      return (current_price - self.entry_price) * self.amount
    elif self.pos_side == PosSide.Short:
      return (self.entry_price - current_price) * self.amount
    return 0.0
  
  @property
  def margin(self) -> float:
    return self.account.get_collateral_margin(self)

  def calculate_mark_price(self, current_price: float) -> float:
    return self.entry_price
  
  def calculate_liq_price(self) -> float:
    if self.pos_side == PosSide.Long:
      return self.entry_price * (1 - 1 / self.leverage)
    elif self.pos_side == PosSide.Short:
      return self.entry_price * (1 + 1 / self.leverage)
    return 0.0
  
  
  def calculate_transact_status(self):
    """根据订单计算交易状态， 更新开仓成本，已实现盈亏和总成本"""
    self.avg_price  = 0.0
    self.total_cost = 0.0
    self.amount = 0.0
    self.realized_pnl = 0.0
    
    for order in self.orders:
      is_opening = True
      match (self.pos_side, order.side):
        case (PosSide.Long, OrderSide.Buy) | (PosSide.Short, OrderSide.Sell):
          is_opening = True
        case (PosSide.Long, OrderSide.Sell) | (PosSide.Short, OrderSide.Buy):
            is_opening = False
        case _:
          is_opening = False
      
      if is_opening:
        # 开仓或加仓逻辑
        fee = 0.0
        if order.comm_settle_asset is order.trading_pair.base:
          fee = order.commission * order.execution_price
          execution_quantity = order.execution_quantity - order.commission
          self.amount += execution_quantity
          trade_cost = execution_quantity * order.execution_price + fee
        else:
          fee = order.commission
          self.amount += order.execution_quantity
          trade_cost = order.execution_quantity * order.execution_price + fee
        
        self.total_cost += trade_cost
        # 重新计算开仓均价
        self.entry_price = self.total_cost / self.amount
        
      else:
        # 平仓或减仓逻辑
        # 注意：平仓不改变 entry_price
        # 在这里可以计算已实现盈亏 (Realized PnL)
        realized_pnl = (order.execution_price - self.entry_price) * order.execution_quantity * (1 if self.pos_side is PosSide.Long else -1)
        if order.comm_settle_asset is order.trading_pair.quote:
          realized_pnl -= order.commission
        else:
          realized_pnl -= order.commission * order.execution_price  
          
        self.realized_pnl = realized_pnl

        self.amount -= order.execution_quantity
        # 减去平仓部分的成本
        self.total_cost = self.entry_price * self.amount

        # 如果全部平仓，重置状态
        if self.amount == 0:
          self.status = PositionStatus.Closed 
          self.total_cost = 0.0
          self.avg_price = 0.0
        

  def __str__(self):
    return "{" + \
      f"\nid: {self.id}," + \
      f"\nentry_price: {self.entry_price}," + \
      f"\namount: {self.amount}," + \
      f"\nstatus: {self.status}," + \
      f"\npos_side: {self.pos_side}," + \
      f"\ntrading_mode: {self.trading_mode}," + \
      f"\nrealized_pnl: {self.realized_pnl}," + \
      f"\nstatus: {self.status}" + \
      "\n}"
