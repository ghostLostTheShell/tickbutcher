
import enum
from tickbutcher.order import Order
from tickbutcher.products import FinancialInstrument


class TradeStatus(enum.Enum):
  Created = 0
  Onchared = 2
  Close = 1
  
class Trade(object):
  """仓位信息 仓位信息是指在Broker处理完毕订单数据后返回仓位信息"""
  id: int
  financial_type:FinancialInstrument
  staus: TradeStatus
  orders: list[Order]  # 该仓位下的所有订单
  
  def __init__(self,id: int, financial_type: FinancialInstrument):
    self.id = id
    self.financial_type = financial_type
    self.orders = []
    
    
  def add_order(self, order: Order):
    self.orders.append(order)
  
  def is_open(self):
    return self.staus is TradeStatus.Onchared
  
  def is_close(self):
    return self.staus is TradeStatus.Close