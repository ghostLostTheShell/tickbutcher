"""
简易版的Buy流程测试
"""

from io import StringIO
import unittest

import pandas as pd

from tickbutcher.brokers import Broker
from tickbutcher.candlefeed import TimeframeType
from tickbutcher.commission import MakerTakerCommission
from tickbutcher.contemplationer import Contemplationer
from tickbutcher.ordermanage import OrderSide
from tickbutcher.ordermanage.ordermanager import OrderManager
from tickbutcher.products import AssetType, FinancialInstrument
from tickbutcher.ordermanage.order import Order, OrderOptionType,OrderProcessStatusType
from ..dataset import sol,btc


# order模块，orderManager 模块， 测试
class CreateOrderAndSubmitOrderUnitTest(unittest.TestCase):
    def test_create_new_order(self):
        new_inancialInstrument =  FinancialInstrument('0001', 'cc', AssetType.STOCK)

        # 买入单
        new_order = Order(new_inancialInstrument,10,OrderSide.Buy,10,OrderOptionType.LimitOrder)
        print(new_order.financial_type.symbol)
        print('create_order')
        print('ID ', new_order.id)
        print('当前执行状态 ', new_order.status)
        print('创建Order的时间 ', new_order.timestamp)
        print('订单个数 ',new_order.quantity)
        print('订单成功交易个数 ',new_order.filled_quantity)
        print('订单剩余个数 ',new_order.remaining_quantity)

        self.assertEqual(True, new_order.is_created())
        print('\n')

        broker1 = Broker('broker1')
        orderManager1 = OrderManager(broker1)
        orderManager1.submit_order(new_order)


        print('order,  new_status')
        print('ID ', new_order.id)
        print('当前执行状态 ', new_order.status)
        print('创建Order的时间 ', new_order.timestamp)
        print('订单个数 ', new_order.quantity)
        print('订单成功交易个数 ', new_order.filled_quantity)
        print('订单剩余个数 ',new_order.remaining_quantity)

        self.assertEqual(True, new_order.is_fill(), '订单全部完成提交')

        print('\n')
        print('\n')

        # 卖出单
        new_order1 = Order(new_inancialInstrument,10,OrderSide.Sell,10, OrderOptionType.LimitOrder)
        print(new_order1.financial_type.symbol)
        print('create_order1')
        print('ID ', new_order1.id)
        print('当前执行状态 ', new_order1.status)
        print('创建Order1的时间 ', new_order1.timestamp)
        print('订单个数 ',new_order1.quantity)
        print('订单成功交易个数 ',new_order1.filled_quantity)
        print('订单剩余个数 ',new_order1.remaining_quantity)

        self.assertEqual(True, new_order1.is_created())
        print('\n')

        broker1 = Broker('broker2')
        orderManager1 = OrderManager(broker1)
        orderManager1.submit_order(new_order1)


        print('order1,  new_status')
        print('ID ', new_order1.id)
        print('当前执行状态 ', new_order1.status)
        print('创建Order1的时间 ', new_order1.timestamp)
        print('订单个数 ', new_order1.quantity)
        print('订单成功交易个数 ', new_order1.filled_quantity)
        print('订单剩余个数 ',new_order1.remaining_quantity)

        self.assertEqual(True, new_order1.is_fill(), '订单全部完成提交')

