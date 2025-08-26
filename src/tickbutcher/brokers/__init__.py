
### broker 中间商

"""
委托-代理关系：
Trader是委托方，发出交易指令。
Broker是代理方，负责执行指令。Broker有法律义务以最佳可能的价格和速度为客户执行订单。

在回测平台上，由Trader调用Broker的方法
那么具体的流程是，在策略中首先实例化一个 trader 类，用于配置order订单和本金信息。
之后在配制完成后，在策略买入条件到达，将调用Broker类的实例进行买入。
那么首先在策略开始就要去实例化 Broker 和 Trader。
（在一般的策略中，会在trader下单时就进行本金的检测，如果Order总价多于本金，则部分买入或者提示本金不足）

（即使挂单失败，策略也可以继续往后跑）
如果Trader的Order设置成功，策略条件达成就可以调用broker实例的buy方法。

进入buy流程
在Broker的Buy流程中，作为代理商要进行订单撮合（BTC似乎是平台有区别）
（现在暂时不考虑撮合，buy的 order全部成功）

* 先不考虑市场滑点的问题，只考虑挂单成功后手续费
那么broker接收到trader的buy Order后，先计算是否 本金  >= 当前k线价格 * 数量 + 总手续费
如果OK就下单买入，那就直接按买入进行处理



#先开发  市价单 (Market Order)   限价单 (Limit Order)   止损单 (Stop Order)
"""
import asyncio
import enum
import time

from tickbutcher.ordermanage.order import Order,OrderSide
from typing import Dict, List, TYPE_CHECKING
from tickbutcher.commission import Commission
from tickbutcher.products import AssetType


### 维护一个订单状态的 Enum
"""
状态	                        含义	                                  需要注意
已创建 (Created)	订单对象已在系统中生成，但可能还未正式发出。	回测中此状态可能很短或不存在。
已提交 (Submitted)	订单已提交给模拟经纪人（Broker）。	意味着回测系统已接收并开始处理该订单。
已接受 (Accepted)	订单已通过初步检查（如资金是否足够），进入排队等待执行或正在执行。	并非所有回测系统都显式有此状态。
部分成交 (Partially Filled)	订单中的一部分数量已经成交。	需记录已成交数和未成交数。剩余部分可能继续等待成交，也可能被撤销。
完全成交 (Filled)	订单的全部数量已经成交。	这是订单成功执行的最终状态之一。需记录成交价格、数量、时间及手续费。
已取消 (Cancelled)	订单在完全成交前被撤销。	这是订单终止状态的其中一种。可能是策略主动撤单，也可能是由于规则（如限价单当日有效）被系统自动撤销。
拒绝 (Rejected)	订单因某种原因未能被接受执行（如下单价格不合理、股票代码错误、可用资金不足等）。	这是订单终止状态的另一种。回测系统应提供拒绝原因，以便调试策略。
已完成 (Completed)	订单生命周期结束	这是一个汇总状态，通常指订单要么完全成交，要么被取消，要么被拒绝，不会再有任何变化。
已失效 (Expired)	订单生命周期结束	订单的最终状态，表示该订单由于未能在其有效期内全部成交，而被系统自动作废。
保证金 (Margin) 开仓和持仓所需的担保资金 ,确保资金和风险管理的真实性。保证金不足会导致新订单被Rejected，根本无法进入等待成交（可能Expired）的队列。
"""

"""
flowchart TD
A[策略创建订单] --> B[状态: 已创建<br>Created]
B --> C[提交至经纪商 Broker]
C --> D[状态: 已提交<br>Submitted]

D --> E{经纪商检查<br>格式与保证金}
E -- 检查通过 --> F[状态: 已接受<br>Accepted<br>**预冻结所需保证金**]
E -- 检查失败 --> G[状态: 拒绝<br>Rejected<br><b>终止状态</b>]

F --> H{等待撮合成交 <br>Padding}
H -- 部分成交 --> I[状态: 部分成交<br>Partially Filled]
I --> H
H -- 全部成交 --> J[状态: 完全成交<br>Filled<br>**正式占用保证金**<br><b>终止状态</b>]

H -- 策略主动撤销 --> K[状态: 已取消<br>Cancelled<br>**释放预冻结保证金**<br><b>终止状态</b>]
H -- 达到有效期未成交 --> L[状态: 已失效<br>Expired<br>**释放预冻结保证金**<br><b>终止状态</b>]

J --> M[状态: 已完成<br>Completed]
K --> M
G --> M
L --> M
"""

"""订单状态类型 （包含准备 and 市商返回类型）"""
class OrderProcessStatusType(enum.Enum):
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




# 在运行时这个导入不会被执行，从而避免循环导入
if TYPE_CHECKING:
    from tickbutcher.contemplationer import Contemplationer


class Broker():
  broker_name:str
  trade_positions:List
  orders:List
  contemplationer:'Contemplationer'
  commission_table:Dict[AssetType, Commission]


  def __init__(self,name: str):
    self.broker_name = None   ## 经济商实例的名称
    self.trade_positions =[]
    self.orders = []    ## 接受的订单
    # ordermanager 的回调函数
    self.order_status_callback = None


  # 由OrderManager调用，注册回调函数
  def set_order_status_callback(self, callback_func):
    self.order_status_callback = callback_func

  async def submit_order(self, order: Order):
    """ 提交订单到真实交易所/模拟引擎 """
    # ... 内部逻辑 ...
    # 当有状态变化时（如接受、成交、取消），调用回调函数通知OrderManager
    # 例如：
    ### 这个变化应该是交易所网络和撮合引擎执行并处理给出返回结果的
    if order.side == OrderSide.Buy.value:
      await self.buy(order)
    if order.side == OrderSide.Sell.value:
      await self.sell(order)
    if order.side == OrderSide.Close.value:
      await self.close_trade(order)


  # 模拟经纪商接受订单
  async def _simulate_order_acceptance(self, order: Order):

    if self.order_status_callback:
      # 这里模拟经纪商在另一个线程/事件循环中异步回调
      await asyncio.sleep(1)
      self.order_status_callback(order.id, OrderProcessStatusType.Accepted.value, 0)

  async def _simulate_order_padding(self, order: Order):
    if self.order_status_callback:
      # 这里模拟经纪商在另一个线程/事件循环中异步回调
      await asyncio.sleep(1)
      self.order_status_callback(order.id, OrderProcessStatusType.Padding.value, 0)

  # 模拟撮合引擎撮合部分完成订单
  async def _simulate_order_partially_filled(self,order: Order):
    await asyncio.sleep(1)
    self.order_status_callback(order.id, OrderProcessStatusType.PartiallyFilled.value, 5)


  # 模拟撮合引擎撮合完成订单
  async def _simulate_order_filled(self,order: Order):
    await asyncio.sleep(1)
    self.order_status_callback(order.id, OrderProcessStatusType.Filled.value, 10)

  """
    在这里涉及到买入流程的设计，无论买卖都需要考虑仓位、手续费、账户内剩余金额信息
    所以是先创建订单，
    再提交订单给Broker 
    Broker收到订单后先预先冻结保证金
    然后Broker再把订单提交至市场 
  """

  ### 参数为订单簿中的单个订单    标的，数量，订单类型(市价单，限价单...)
  async def buy(self, single_order : Order) :
    self.orders = []
    self.commission_table = {}
    print('订单方向Buy',single_order.side)
    # 接收
    await self._simulate_order_acceptance(single_order)
    print('Buy订单流程状态1', single_order.status)
    # 等待
    await self._simulate_order_padding(single_order)
    print('Buy订单流程状态2', single_order.status)
    # 下单
    await self._simulate_order_filled(single_order)
    print('Buy订单流程状态3', single_order.status)

    # 执行完成

  async def sell(self, single_order : Order):
    print(single_order.side)
    # 接收
    await self._simulate_order_acceptance(single_order)
    print('Sell订单流程状态1 ', single_order.status)
    # 等待
    await self._simulate_order_padding(single_order)
    print('Sell订单流程状态2', single_order.status)

    # 下单
    await self._simulate_order_filled(single_order)
    print('Sell订单流程状态3', single_order.status)

    # 执行完成

  def close_trade(self, trade_position):
    """平仓"""
    pass



  def set_contemplationer(self, contemplationer: 'Contemplationer'):
    self.contemplationer = contemplationer

  def set_commission(self, asset_type: AssetType, commission: Commission):
    self.commission_table[asset_type] = commission
    
  def get_commission(self, asset_type: AssetType) -> Commission:
    return self.commission_table[asset_type]

  def next(self):
    pass