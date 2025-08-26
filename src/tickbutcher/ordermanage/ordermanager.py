"""
订单管理器（Order Manager）
OrderManager 作为策略和经纪商之间的中间人，负责：

维护所有订单的列表（“order列表”）。
将策略的订单请求发送给经纪商Broker。
接收来自经纪商Broker的订单状态更新。
根据状态更新，决定是否需要执行后续操作（如继续执行未完成订单）。


建立一个事件驱动的系统，让Broker主动通知，由订单管理器来智能响应。
Broker和市商交易完成后，将调用订单管理方法将订单数据传给这个类，然后再去修改对应的订单状态信息。
"""
import asyncio
from tokenize import String
from typing import Dict

from tickbutcher.brokers import Broker
from tickbutcher.ordermanage import OrderProcessStatusType
from tickbutcher.ordermanage.order import Order


class OrderManager:
    # open_orders: Dict[String, Order]

    # 接受策略中创建的broker实例
    def __init__(self, broker: Broker):
        self.open_orders = {}  # 活跃订单字典: order_id -> Order Object
        self.all_orders = []  # 所有订单的历史列表
        self.broker = broker  # 经纪商实例

        # 向经纪商注册回调函数，这样经纪商有任何更新都会通知到OrderManager
        self.broker.set_order_status_callback(self.on_order_status_update)

    def submit_order(self, new_order: Order):
        """ 接收来自策略的订单请求 """
        # 1. 创建订单对象

        self.open_orders[new_order.id] = new_order
        self.all_orders.append(new_order)

        # 2. 通过经纪商提交订单
        try:
            new_order.status = OrderProcessStatusType.Submitted.value
            asyncio.run(self.broker.submit_order(new_order))
        except Exception as e:
            new_order.status = OrderProcessStatusType.Rejected.value
            # 通知策略...


    # order_id   订单ID, new_status 更新后订单状态, filled_quantity 订单完成数量
    def on_order_status_update(self, order_id, new_status : OrderProcessStatusType, filled_quantity, **kwargs):
        order = self.open_orders.get(order_id)
        if not order:
            print("找不到对应订单ID为：", order_id, " 的订单")
            return

        old_status = order.status
        order.status = new_status  # 修改order实例状态
        order.filled_quantity = filled_quantity #修改order实例内挂单成交数量
        order.remaining_quantity = order.quantity - order.filled_quantity # 计算未挂单单量
        order.quantity = order.remaining_quantity # 修改订单数量为未挂单数量

        if new_status == OrderProcessStatusType.PartiallyFilled:
            self._handle_partial_fill(order)

        elif new_status == OrderProcessStatusType.Filled:
            self._handle_fill(order)
            self._clean_up_order(order)   # 从open_orders订单簿中移除

        elif new_status == OrderProcessStatusType.Cancelled:
            # 如果订单的旧状态为部分成交
            if old_status == OrderProcessStatusType.PartiallyFilled:
                self._handle_partial_cancel(order)
            self._clean_up_order(order)

        elif new_status == "Rejected":
            self._clean_up_order(order)


    def _handle_partial_fill(self, order: Order):
        """ 处理部分成交 """
        # 1. 更新本地持仓和资金计算（释放部分预冻结保证金？）
        # 2. 检查是否需要自动创建新订单来补足剩余数量？
        #    例如：策略希望无论如何都要完全成交，可以在这里触发一个新的限价单/市价单
        remaining_quantity = order.quantity - order.filled_quantity
        # if self.strategy.continue_on_partial_fill: # 示例逻辑
        #     new_order_request = ... # 创建新的订单请求，数量为remaining_qty
        #     self.place_order(new_order_request)
        print(f"Order {order.order_id} partially filled. Filled: {order.filled_quantity}, Remaining: {remaining_quantity}")

    def _handle_fill(self, order: Order):
        """ 处理完全成交 """
        # 更新投资组合：正式占用保证金，增加持仓
        order.filled_quantity = order.quantity
        order.quantity = 0
        print(f"Order {order.order_id} fully filled.")

    def _handle_partial_cancel(self, order: Order):
        """ 处理部分成交后的取消 """
        # 处理部分成交后剩下的部分被取消的逻辑
        remaining_quantity = order.quantity - order.filled_quantity
        # 释放剩余数量的预冻结保证金
        print(f"Order {order.id} partially cancelled. {remaining_quantity} units cancelled after partial fill.")

    def _clean_up_order(self, order : Order):
        """ 订单终结处理 """
        if order.is_done():
            self.open_orders.pop(order.id, None)

    def _notify_strategy(self, order : Order, old_status : OrderProcessStatusType, new_status : OrderProcessStatusType):
        # 这里可以通过回调函数、消息队列、事件总线等方式通知策略
        # 例如：self.strategy.on_order_event(order, old_status, new_status)
        print(f"Order {order.id} updated: {old_status} -> {new_status}")





