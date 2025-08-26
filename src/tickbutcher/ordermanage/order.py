import enum
import uuid
from datetime import datetime

from tickbutcher.ordermanage import OrderOptionType, OrderProcessStatusType, OrderSide
from tickbutcher.products import FinancialInstrument

### 单个订单的类型
class Order():
  def __init__(self, financial_type:FinancialInstrument, quantity:int, side: OrderSide ,price:float, orderOptionType: OrderOptionType):
    self.id = uuid.uuid1()   # 使用UUID确保唯一性，接入实盘可以使用市商传来的订单号
    self.financial_type = financial_type   ### 标的类型 symbol 标的， id， 产品类型 （期货or股票or币... ）
    self.quantity = quantity   ### 数量
    self.price = price     ### 价格
    self.order_optionType = orderOptionType.value  ### 订单操作类型
    self.filled_quantity = 0.0  # 已成交数量，被市场接受的数量
    self.remaining_quantity = quantity # 未成交数量，未市场接受的数量
    self.side = side.value # buy or sell or close
    self.status = OrderProcessStatusType.Created.value  # 当前的订单状态，实例化就为Create
    self.timestamp = int(datetime.now().timestamp())  # 订单实例化时的时间

  # 判断当前的order状态是否还有机会进行处理
  def is_created(self):
    return self.status == OrderProcessStatusType.Created.value

  def is_active(self):
    return self.status in (OrderProcessStatusType.Submitted.value,
                           OrderProcessStatusType.Accepted.value,
                           OrderProcessStatusType.PartiallyFilled.value,
                           OrderProcessStatusType.Padding.value)

  # 判断当前order状态是否已经失败终结
  def is_done(self):
    return self.status in (OrderProcessStatusType.Cancelled.value,
                           OrderProcessStatusType.Rejected.value,
                           OrderProcessStatusType.Margin.value)

  # 判断当前order是否全部成交
  def is_fill(self):
    return self.status == OrderProcessStatusType.Filled.value

  # 判断当前order是否处于市商撮合的等待状态
  def is_padding(self):
    return self.status == OrderProcessStatusType.Padding.value