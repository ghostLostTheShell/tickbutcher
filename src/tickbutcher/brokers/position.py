
import enum
from typing import TYPE_CHECKING, Dict

from tickbutcher.order import *
from tickbutcher.products import AssetType

# 在运行时这个导入不会被执行，从而避免循环导入
if TYPE_CHECKING:
  from tickbutcher.brokers.trading_pair import TradingPair
  from tickbutcher.products import FinancialInstrument
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
  base: 'FinancialInstrument' #基础货币
  status: PositionStatus
  orders: list['Order']  # 该仓位下的所有订单
  buy_orders: list['Order']  # 该仓位下的所有买入订单
  sell_orders: list['Order']  # 该仓位下的所有卖出订单
  amount: float  # 仓位数量/大小
  entry_price: float  # 开仓均价/持仓均价
  mark_price: float  # 标记价格
  unrealized_pnl: float  # 未实现盈亏
  # realized_pnl: float  # 已实现盈亏
  leverage: float  # 杠杆倍数
  margin: float  # 保证金
  liq_price: float  # 强平价格/爆仓价(liquidation_price)
  pos_side: 'PosSide'  # 持仓方向，LONG (多头), SHORT (空头), 或 单方向仓
  trading_mode: 'TradingMode'  # 交易模式，逐仓或全仓,现金
  ps_funding: float  # 永续合约的资金费用
  settlement_records: Dict['Order', float]  # 结算记录, key是订单，value是结算金额(持仓均价)

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
    self.amount = 0.0
    self.entry_price = 0.0
    self.mark_price = 0.0
    self.buy_orders = []
    self.sell_orders = []
    self.settlement_records = {}

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
        #
        # 计算持仓均价
        # 采用移动加权平均法(加上手续费)
        base = order.trading_pair.base
        
        self.amount = sum((o.execution_quantity - o.commission if o.comm_settle_asset is base else o.execution_quantity) for o in self.buy_orders)
        self.entry_price = sum(o.execution_price * (o.execution_quantity - o.commission  if o.comm_settle_asset is base else o.execution_quantity ) for o in self.buy_orders) / self.amount

      case (PosSide.Long, OrderSide.Sell):
        # 计算平仓
        # 判断仓位是否是全平
        if order.execution_quantity >= self.amount:
          self.status = PositionStatus.Closed
          self.amount = 0.0

        else:
          pass

        self.settlement_records[order] = self.entry_price


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
    if self.trading_mode != TradingMode.Isolated:
      raise ValueError("Can only add margin in isolated mode")
    self.margin += amount
    
  def reduce_margin(self, amount: float):
    if self.trading_mode != TradingMode.Isolated:
      raise ValueError("Can only reduce margin in isolated mode")
    self.margin -= amount
    
 
  def calculate_unrealized_pnl(self, current_price: float) -> float:
    """
    计算未实现盈亏
    """
    if self.status != PositionStatus.Active:
      return 0.0

    match (self.base.type, self.pos_side):

      case (AssetType.PerpetualSwap, PosSide.Long):
          return (current_price - self.entry_price) * self.amount - self.ps_funding
        
      case (AssetType.PerpetualSwap, PosSide.Short):
          return (self.entry_price - current_price) * self.amount - self.ps_funding
      
      case _:
        return (current_price - self.entry_price) * self.amount

  def calculate_mark_price(self, current_price: float) -> float:
    return self.entry_price
  
  def calculate_liq_price(self) -> float:
    if self.pos_side == PosSide.Long:
      return self.entry_price * (1 - 1 / self.leverage)
    elif self.pos_side == PosSide.Short:
      return self.entry_price * (1 + 1 / self.leverage)
    return 0.0
  
  @property
  def realized_pnl(self):
    realized_pnl = 0.0
    for order, entry_price in self.settlement_records.items():
      a = entry_price * order.execution_quantity
      b = order.execution_price * order.execution_quantity
      realized_pnl += abs(a - b) 
      if order.comm_settle_asset is order.trading_pair.quote:
        realized_pnl -= order.commission

    return abs(realized_pnl)
