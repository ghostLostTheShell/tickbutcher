"""
订单管理器（Order Manager）
OrderManager 作为策略和经纪商之间的中间人，负责：

维护所有订单的列表（“order列表”）。
将策略的订单请求发送给经纪商Broker。
接收来自经纪商Broker的订单状态更新。
根据状态更新，决定是否需要执行后续操作（如继续执行未完成订单）。


建立一个事件驱动的系统，让Broker主动通知，由订单管理器来智能响应。
"""


class OrderManager:
    def __init__(self, broker):
        self.open_orders = {}  # 活跃订单字典: order_id -> Order Object
        self.all_orders = []  # 所有订单的历史列表
        self.broker = broker  # 经纪商实例
        # 向经纪商注册回调函数，这样经纪商有任何更新都会通知我们
        self.broker.set_order_status_callback(self.on_order_status_update)

    def place_order(self, order_request):
        """ 接收来自策略的订单请求 """
        # 1. 创建订单对象
        new_order = Order
        new_order.status = "Created"
        self.open_orders[new_order.order_id] = new_order
        self.all_orders.append(new_order)

        # 2. 通过经纪商提交订单
        try:
            self.broker.submit_order(new_order)
            new_order.status = "Submitted"
        except Exception as e:
            new_order.status = "Rejected"
            # 通知策略...

    def on_order_status_update(self, order_id, new_status, filled_qty, **kwargs):
        """ 经纪商回调函数：处理订单状态更新 """
        order = self.open_orders.get(order_id)
        if not order:
            return  # 找不到订单，记录日志

        old_status = order.status
        order.status = new_status
        order.filled_quantity = filled_qty

        # --- 状态处理逻辑的核心 ---
        if new_status == "PartiallyFilled":
            self._handle_partial_fill(order)

        elif new_status == "Filled":
            self._handle_fill(order)
            self._clean_up_order(order)  # 从open_orders中移除

        elif new_status == "Cancelled":
            if old_status == "PartiallyFilled":
                self._handle_partial_cancel(order)
            self._clean_up_order(order)

        elif new_status == "Rejected":
            self._clean_up_order(order)

        # 通知策略（或其他组件）状态发生了变化
        self._notify_strategy(order, old_status, new_status)