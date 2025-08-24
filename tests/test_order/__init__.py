from io import StringIO
import unittest

import pandas as pd
from tickbutcher.candlefeed import TimeframeType
from tickbutcher.commission import MakerTakerCommission
from tickbutcher.contemplationer import Contemplationer
from tickbutcher.products import AssetType, FinancialInstrument
from tickbutcher.ordermanage.order import Order, OrderOptionType,OrderProcessStatusType
from ..dataset import sol,btc

# order模块，orderManager 模块， 测试
class OrderUnitTest(unittest.TestCase):
    def test_create_new_order(self):
        new_inancialInstrument =  FinancialInstrument('0001', 'cc', AssetType.STOCK)
        new_order = Order(new_inancialInstrument,10,'Buy',10,OrderOptionType.LimitOrder)
        print(new_order.id)
        print(new_order.timestamp)

        new_inancialInstrument =  FinancialInstrument('0002', 'cc1', AssetType.BOND)
        new_order2 = Order(new_inancialInstrument, 10, 'Buy', 10, OrderOptionType.LimitOrder)
        print(new_order2.financial_type.symbol)
        print(new_order2.id)
        print(new_order2.status)
        print(new_order2.timestamp)

