
import unittest

from tickbutcher.products import AssetType, FinancialInstrument
from tickbutcher.products import common

class FinancialInStrumentUnitTest(unittest.TestCase):
  
  def test_create(self):
    instrument = FinancialInstrument(symbol="Test Instrument", type=AssetType.STOCK)
    
    value_error = None
    try:
      FinancialInstrument(symbol="Test Instrument", type=AssetType.FUTURE)
    except ValueError as err:
      value_error = err

    # Assert that a ValueError was raised
    self.assertIsInstance(value_error, ValueError)
    # 检查 symbol 是否正确
    self.assertEqual(instrument.symbol, "Test Instrument")
    # 检查new同一个symbol是否一致
    btc = FinancialInstrument(symbol="BTC", type=AssetType.CRYPTO)
    common.BTC = btc
    self.assertEqual(common.BTC, btc)
  
  def test_get_by_symbol(self):
    """测试get_by_symbol方法"""
    # 测试获取已存在的symbol
    usdt_instance = FinancialInstrument.get_by_symbol("USDT")
    self.assertIsNotNone(usdt_instance)
    self.assertEqual(usdt_instance.symbol, "USDT")
    self.assertEqual(usdt_instance, common.USDT)
    
    btc_instance = FinancialInstrument.get_by_symbol("BTC")
    self.assertIsNotNone(btc_instance)
    self.assertEqual(btc_instance.symbol, "BTC")
    self.assertEqual(btc_instance, common.BTC)
    
    eth_instance = FinancialInstrument.get_by_symbol("ETH")
    self.assertIsNotNone(eth_instance)
    self.assertEqual(eth_instance.symbol, "ETH")
    self.assertEqual(eth_instance, common.ETH)
    
    # 测试获取不存在的symbol应该抛出KeyError
    with self.assertRaises(KeyError) as context:
      FinancialInstrument.get_by_symbol("UNKNOWN_SYMBOL")
    
    self.assertIn("UNKNOWN_SYMBOL", str(context.exception))
    
    