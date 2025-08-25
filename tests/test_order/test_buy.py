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
from tickbutcher.ordermanage.ordermanager import OrderManager
from tickbutcher.products import AssetType, FinancialInstrument
from tickbutcher.ordermanage.order import Order, OrderOptionType,OrderProcessStatusType
from ..dataset import sol,btc


# order模块，orderManager 模块， 测试
class CreateOrderAndSubmitOrderUnitTest(unittest.TestCase):
    def test_create_new_order(self):
        new_inancialInstrument =  FinancialInstrument('0001', 'cc', AssetType.STOCK)
        new_order = Order(new_inancialInstrument,10,'Buy',10,OrderOptionType.LimitOrder)
        print(new_order.financial_type.symbol)
        print('new_order')
        print('ID ', new_order.id)
        print('当前执行状态 ', new_order.status)
        print('创建Order的时间 ', new_order.timestamp)
        print('订单个数 ',new_order.quantity)
        print('订单成功交易个数 ',new_order.filled_quantity)

        print('\n')

        broker1 = Broker()
        orderManager1 = OrderManager(broker1)
        orderManager1.place_order(new_order)




        print('new_order  new_status')
        print('ID ', new_order.id)
        print('当前执行状态 ', new_order.status)
        print('创建Order的时间 ', new_order.timestamp)
        print('订单个数 ', new_order.quantity)
        print('订单成功交易个数 ', new_order.filled_quantity)


