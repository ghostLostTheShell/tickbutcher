import unittest
from tickbutcher.products import AssetType, FinancialInstrument
from ..dataset import sol,btc

# order模块，orderManager 模块， 测试
class OrderUnitTest(unittest.TestCase):
    def test_create_new_order(self):
      self.assertEqual(True, True)
