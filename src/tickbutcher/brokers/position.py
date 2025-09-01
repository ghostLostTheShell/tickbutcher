
import enum
from typing import TYPE_CHECKING

from tickbutcher.order import OrderSide


# 在运行时这个导入不会被执行，从而避免循环导入
if TYPE_CHECKING:
  from tickbutcher.brokers.trading_pair import TradingPair
  from tickbutcher.order import Order
  from tickbutcher.order import TradingMode
  from tickbutcher.order import PosSide
  from tickbutcher.products import FinancialInstrument
class PositionStatus(enum.Enum):
  Active = 0  #持仓中
  Closed = 1  #已平仓
  ForcedLiq = 2  #强制平仓（ForcedLiquidation）

class Position(object):
  """仓位信息 仓位信息是指在Broker处理完毕订单数据后返回仓位信息"""
  id: int
  trading_pair: 'TradingPair' #用于记录合约期货类产品是用哪个交易对的
  base: 'FinancialInstrument' #基础货币
  status: PositionStatus
  orders: list['Order']  # 该仓位下的所有订单
  buy_orders: list['Order']  # 该仓位下的所有买入订单
  sell_orders: list['Order']  # 该仓位下的所有卖出订单
  amount: float  # 仓位数量/大小
  entry_price: float  # 开仓均价/持仓均价
  mark_price: float  # 标记价格
  unrealized_pnl: float  # 未实现盈亏
  realized_pnl: float  # 已实现盈亏
  leverage: float  # 杠杆倍数
  margin: float  # 保证金
  liq_price: float  # 强平价格/爆仓价(liquidation_price)
  pos_side: 'PosSide'  # 持仓方向，LONG (多头), SHORT (空头), 或 单方向仓
  trading_mode: 'TradingMode'  # 交易模式，逐仓或全仓,现金
  ps_funding: float  # 永续合约的资金费用

  def __init__(self, 
               id: int,
               *,
               base: 'FinancialInstrument',
               pos_side: 'PosSide',
               trading_mode: 'TradingMode',
               ):
    self.id = id
    self.base = base
    self.orders = []
    self.status = PositionStatus.Active
    self.pos_side = pos_side
    self.trading_mode = trading_mode

  def set_trading_pair(self, trading_pair: 'TradingPair'):
    self.trading_pair = trading_pair

  def add_order(self, order: 'Order'):
    #计算持仓均价
    
    
    if order not in self.orders:
      self.orders.append(order)
    match order.side:
      case OrderSide.Buy:
        self.buy_orders.append(order)
      case OrderSide.Sell:
        self.sell_orders.append(order)

    match (self.pos_side, order.side):
      case (PosSide.Long, OrderSide.Buy):
        self.amount = sum(o.execution_quantity for o in self.buy_orders)
        self.entry_price = sum(o.execution_price * o.execution_quantity for o in self.buy_orders) / self.amount

      case (PosSide.Long, OrderSide.Sell):
        # 计算平仓
        # 判断仓位是否是全平
        if order.execution_quantity >= self.amount:
          self.status = PositionStatus.Closed
          
                  
        
      case (PosSide.Short, OrderSide.Buy):
        self.amount = sum(o.execution_quantity for o in self.buy_orders)
        self.entry_price = sum(o.execution_price * o.execution_quantity for o in self.buy_orders) / self.amount

      case (PosSide.Short, OrderSide.Sell):
        self.amount = sum(o.execution_quantity for o in self.sell_orders)
        self.entry_price = sum(o.execution_price * o.execution_quantity for o in self.sell_orders) / self.amount

      case _:
        raise ValueError(f"Unknown position side: {self.pos_side}")

    

  def is_active(self):
    return self.status is PositionStatus.Active

  def is_closed(self):
    return self.status in (PositionStatus.Closed, PositionStatus.ForcedLiq)

  def add_margin(self, amount: float):
    self.margin += amount
    
  def reduce_margin(self, amount: float):
    self.margin -= amount
    
  #计算盈利
  def calculate_profit(self, current_price: float) -> float:
    if self.pos_side == PosSide.Long:
      return (current_price - self.entry_price) * self.amount
    elif self.pos_side == PosSide.Short:
      return (self.entry_price - current_price) * self.amount
    return 0.0


  def calculate_mark_price(self, current_price: float) -> float:
    return self.entry_price
  
  def calculate_liq_price(self) -> float:
    if self.pos_side == PosSide.Long:
      return self.entry_price * (1 - 1 / self.leverage)
    elif self.pos_side == PosSide.Short:
      return self.entry_price * (1 + 1 / self.leverage)
    return 0.0
  