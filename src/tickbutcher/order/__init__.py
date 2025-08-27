import enum
import uuid
from datetime import datetime
from tickbutcher.order import OrderType, OrderStatus, OrderSide
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


class Order():
  id: int
  financial_type: FinancialInstrument
  quantity: float # 下单数量
  side: OrderSide
  price: float # 下单价格
  order_option_type: OrderType
  
  execution_price:float   # 成交价格
  execution_quantity:float  # 成交数量 
  status:OrderStatus

  def __init__(self, 
               financial_type:FinancialInstrument, 
               quantity:int, 
               side: OrderSide,
               price:float, 
               order_option_type: OrderType):
    
    self.financial_type = financial_type    ### 标的类型 symbol 标的， id， 产品类型 （期货or股票or币... ）
    self.quantity = quantity                ### 数量
    self.price = price                      ### 价格
    self.order_option_type = order_option_type  ### 订单操作类型
    self.filled_quantity = 0.0                  # 已成交数量，被市场接受的数量
    self.remaining_quantity = quantity           # 未成交数量，未市场接受的数量
    self.side = side                             # buy or sell
    self.status = OrderStatus.Created  # 当前的订单状态，实例化就为Create

  
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