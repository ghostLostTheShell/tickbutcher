
import enum


from typing import TYPE_CHECKING
# 在运行时这个导入不会被执行，从而避免循环导入
if TYPE_CHECKING:
  from tickbutcher.brokers.trading_pair import TradingPair
  from tickbutcher.order import Order

class PositionStatus(enum.Enum):
  Open = 0  #持仓中
  Closed = 1  #已平仓
  ForcedLiquidation = 2  #强制平仓

class Position(object):
  """仓位信息 仓位信息是指在Broker处理完毕订单数据后返回仓位信息"""
  id: int
  tradingPair: 'TradingPair'
  status: PositionStatus
  orders: list['Order']  # 该仓位下的所有订单
  margin: float
  amount: float  # 仓位数量/大小
  entry_price: float  # 开仓均价/持仓均价
  mark_price: float  # 标记价格
  unrealized_pnl: float  # 未实现盈亏
  leverage: float  # 杠杆倍数
  margin: float  # 保证金
  initial_margin: float  # 起始保证金
  maintenance_margin: float  # 维持保证金
  liquidation_price: float  # 强平价格/爆仓价
  position_side: str  # 持仓方向，LONG (多头), SHORT (空头), 或 BOTH (双向持仓模式下)

  def __init__(self,id: int, tradingPair: 'TradingPair'):
    self.id = id
    self.tradingPair = tradingPair
    self.orders = []
    self.status = PositionStatus.Open
    


  def add_order(self, order: 'Order'):
    self.orders.append(order)
  
  def is_open(self):
    return self.status is PositionStatus.Open

  def is_close(self):
    return self.status is PositionStatus.Closed