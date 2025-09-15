
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

from typing import Dict, List
from tickbutcher.brokers import Broker
from tickbutcher.commission import Commission
from tickbutcher.AlphaHub import AlphaHub
from tickbutcher.order import Order, OrderStatus, OrderSide
from tickbutcher.products import AssetType


class MatchingEngineBroker(Broker):
  broker_name:str
  trade_positions:List
  orders:List
  AlphaHub:'AlphaHub'
  commission_table:Dict[AssetType, Commission]


  def __init__(self,name: str):
    self.broker_name = None   ## 经济商实例的名称
    self.trade_positions =[]
    self.orders = []    ## 接受的订单
    # ordermanager 的回调函数
    self.order_status_callback = None
    self.commission_table = {}


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
      self.order_status_callback(order.id, OrderStatus.Accepted.value, 0)

  async def _simulate_order_padding(self, order: Order):
    if self.order_status_callback:
      # 这里模拟经纪商在另一个线程/事件循环中异步回调
      self.order_status_callback(order.id, OrderStatus.Padding.value, 0)

  # 模拟撮合引擎撮合部分完成订单
  async def _simulate_order_partially_filled(self,order: Order):
    self.order_status_callback(order.id, OrderStatus.PartiallyFilled.value, 5)


  # 模拟撮合引擎撮合完成订单
  async def _simulate_order_filled(self,order: Order):
    self.order_status_callback(order.id, OrderStatus.Filled.value, 10)

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





