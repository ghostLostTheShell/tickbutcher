# 简易撮合引擎
import heapq
from typing import List, Dict

from tickbutcher.order import Order, OrderSide, OrderType,OrderStatus


class MatchingEngine:
    def __init__(self):
        # 买盘订单簿（最大堆）：价格高的优先，同价时间早的优先
        self.bids: List[Order] = []
        # 卖盘订单簿（最小堆）：价格低的优先，同价时间早的优先
        self.asks: List[Order] = []
        # 所有订单的映射
        self.orders: Dict[str, Order] = {}
        # 成交历史
        self.trade_history: List[Order] = []

    def add_order(self, order: Order) -> List[Order]:
        """添加新订单并尝试撮合，返回生成的交易列表"""
        self.orders[order.id] = order
        trades = []


        if order.side == OrderSide.Buy.value:
            # 处理买单：尝试与卖盘订单匹配
            trades = self._match_buy_order()
            # 如果还有剩余数量且是限价单，加入买盘订单簿
            if order.remaining_quantity > 0  and order.order_optionType == OrderType.LimitOrder.value:
                heapq.heappush(self.bids, order)
        elif order.side == OrderSide.Sell.value:
            # 处理卖单：尝试与买盘订单匹配
            trades = self._match_sell_order(order)
            # 如果还有剩余数量且是限价单，加入卖盘订单簿
            if order.remaining_quantity > 0 and order.order_optionType == OrderType.LimitOrder.value:
                heapq.heappush(self.asks, order)

        elif order.side == OrderSide.Close.value:
            pass

        return trades



    def _match_buy_order(self, buy_order: Order) -> List[Order]:
        """尝试撮合买单与卖盘订单"""
        trades = []
        while(buy_order.remaining_quantity and self.asks and (
          (buy_order.order_optionType == OrderType.MarketOrder.value or
           (buy_order.price is not None and buy_order.price >= self.asks[0].price)))):
            ## 订单簿中第一个卖单
            best_ask = self.asks[0]
            trade_price = best_ask.price # 使用卖单价格成交
            trade_quantity = min(buy_order.remaining_quantity, best_ask.remaining_quantity)

            trades.append(buy_order)

            buy_order.quantity = trade_quantity
            buy_order.price = trade_price
            best_ask.fill(trade_quantity, trade_price)

            # 如果卖单已全部成交，从订单簿中移除
            if best_ask.status == OrderStatus.Filled.value:
                heapq.heappop(self.asks)







    def _match_sell_order(self, sell_order: Order) -> List[Order]:

        """尝试撮合卖单与买盘订单"""
        trades = []

        while (sell_order.remaining_quantity > 0 and self.bids and
               (sell_order.order_optionType == OrderType.MarketOrder or
                (sell_order.price is not None and sell_order.price <= self.bids[0].price))):

            best_bid = self.bids[0]
            trade_price = best_bid.price  # 使用买单价格成交
            trade_quantity = min(sell_order.remaining_quantity, best_bid.remaining_quantity)

            trades.append(sell_order)

            # 如果买单已全部成交，从订单簿中移除
            if best_bid.status == OrderStatus.Filled.value:
                heapq.heappop(self.bids)



    def cancel_order(self, order_id: str) -> bool:
        # 取消订单
        if order_id not in self.orders:
            return False

        order = self.orders[order_id]

        if order.status not in [OrderStatus.Padding.value, OrderStatus.PartiallyFilled.value]:
            return False
        # 从订单簿中移除（如果存在）
        if order in self.bids:
            self.bids.remove(order)
            heapq.heapify(self.bids)

        elif order in self.asks:
            self.asks.remove(order)
            heapq.heapify(self.asks)

        order.status = OrderStatus.Cancelled.value



    def get_order_book(self, depth: int = 5) -> Dict:
        """获取订单簿快照"""
        # 买盘：价格从高到低
        bids = []
        for i, order in enumerate(
                sorted(self.bids, key=lambda x: (-x.price if x.price else float('-inf'), x.timestamp))):
            if i >= depth:
                break
            bids.append({
                'price': order.price,
                'quantity': order.remaining_quantity,
                'order_id': order.order_id
            })

        # 卖盘：价格从低到高
        asks = []
        for i, order in enumerate(sorted(self.asks, key=lambda x: (x.price if x.price else float('inf'), x.timestamp))):
            if i >= depth:
                break
            asks.append({
                'price': order.price,
                'quantity': order.remaining_quantity,
                'order_id': order.order_id
            })

        return {'bids': bids, 'asks': asks}




