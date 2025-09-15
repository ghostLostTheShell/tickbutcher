
import unittest

from tickbutcher.products import AssetType, FinancialInstrument
from tickbutcher.products import common

class FinancialInStrumentUnitTest(unittest.TestCase):
  
  def test_create(self):
    instrument = FinancialInstrument(symbol="Test Instrument", type=AssetType.STOCK)
    
    value_error:ValueError = None
    try:
      instrument_1 = FinancialInstrument(symbol="Test Instrument", type=AssetType.FUTURE)
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
    
    