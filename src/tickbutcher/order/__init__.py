import enum
from typing import Optional, TYPE_CHECKING


if TYPE_CHECKING:
  from tickbutcher.brokers.account import Account
  from tickbutcher.brokers.trading_pair import TradingPair
  from tickbutcher.products import FinancialInstrument
class OrderType(enum.Enum):
  """订单操作类型"""
  MarketOrder = 1  # 市价单
  LimitOrder = 2 # 限价单
  StopOrder = 3
  StopLimitOrder = 4
  TrailingStopOrder = 5
  Iceberg_Order = 6
  FillOrKillOrder = 7
  ImmediateOrCancelOrder = 8
  PostOnlyOrder = 9
  OneCancelsTheOtherOrder = 10
  TWAPOrder = 11


class OrderStatus(enum.Enum):
  """订单状态类型 （包含准备 and 市商返回类型）"""
  Created = 0       ### 已创建 (Created)
  Submitted = 1   ### 已提交 (Submitted)
  Padding = 2  ### 等待订单撮合 (Padding)
  Accepted = 3 ### 已接受 (Accepted) 预先扣除保证金
  PartiallyFilled = 4   ### 部分成交 (Partially Filled)
  Filled = 5   ### 完全成交 (Filled)
  Cancelled = 6   ### 已取消 (Cancelled)
  Rejected = 7   ### 拒绝 (Rejected)
  Completed = 8   ### 已完成 (Completed) 订单全部完成
  Expired = 9  ### 已失效 (Expired)
  Margin = 10  ### 保证金不足 （Margin）

'''操作方向'''
class OrderSide(enum.Enum):
  Buy = 0
  Sell = 1
  
class PosSide(enum.Enum):
  """订单操作仓位方向"""
  Long = 0
  Short = 1
  NET = 3
  
class TradingMode(enum.Enum):
  """交易模式"""
  Isolated = 0
  Cross = 1
  Cash = 2

class Order():
  id: int
  trading_pair: 'TradingPair' # 交易对
  quantity: float           # 下单数量
  side: OrderSide           # 买卖方向
  price: Optional[float]    # 委托价格
  order_type: OrderType     # 订单类型
  execution_price:float       # 成交价格
  execution_quantity:float    # 成交数量
  status:OrderStatus          # 订单状态
  created_at: int             # 订单创建时间
  completed_at: int           # 订单结束时间
  account: 'Account'          # 该订单所属的账户
  trading_mode:TradingMode    #交易模式
  pos_side:Optional[PosSide]    #仓位方向
  reduce_only:Optional[float]   #仅减仓
  commission:float              #手续费
  comm_settle_asset:'FinancialInstrument' # 手续费结算资产

  def __init__(self, 
               *,
               trading_mode:TradingMode,
               trading_pair:'TradingPair',
               quantity:float, 
               side: OrderSide,
               order_type: OrderType,
               account: 'Account',
               pos_side:Optional[PosSide]   =None,
               price: Optional[float]       = None,
               reduce_only:Optional[float]  = None
               ):

      self.trading_pair = trading_pair
      self.quantity = quantity
      self.price = price
      self.order_type = order_type
      self.execution_price = 0.0
      self.execution_quantity = 0.0
      self.status = OrderStatus.Created
      self.side = side
      self.account = account
      self.trading_mode=trading_mode
      self.pos_side = pos_side
      self.reduce_only=reduce_only
  
  def is_created(self):
    """判断当前的order状态是否还有机会进行处理"""
    return self.status is OrderStatus.Created

  def is_active(self):
    return self.status in (OrderStatus.Submitted,
                           OrderStatus.Accepted,
                           OrderStatus.PartiallyFilled,
                           OrderStatus.Padding)

  def set_id(self, id: int):
    self.id = id

  def add_execution_quantity(self, quantity: float):
    self.execution_quantity += quantity

  def is_done(self):
    """判断当前order是否已经结束"""
    return self.status in (OrderStatus.Cancelled,
                           OrderStatus.Rejected,
                           OrderStatus.Margin)

  def is_fill(self):
    """判断当前order是否全部成交"""
    return self.status == OrderStatus.Filled

  def is_padding(self):
    """判断当前order是否处于市商撮合的等待状态"""
    return self.status == OrderStatus.Padding
  
  def set_commission(self, 
                     commission:float, 
                     settle_asset:'FinancialInstrument'):
    self.commission = commission
    self.comm_settle_asset = settle_asset
    