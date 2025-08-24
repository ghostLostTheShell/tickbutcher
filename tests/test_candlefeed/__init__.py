from io import StringIO
import unittest
import pandas as pd
from tickbutcher.candlefeed import CandleFeedDB, CandleFeedProxy, TimeframeType
from tickbutcher.commission import MakerTakerCommission
from tickbutcher.products import AssetType, FinancialInstrument
from ..dataset import sol,btc

class CandlefeedUnitTest(unittest.TestCase):
  
  def test_candle_feed_proxy(self):
    sol_df = pd.read_json(StringIO(sol.USDT_T_SOL), convert_dates=False).set_index('timestamp')
    btc_df = pd.read_json(StringIO(btc.USDT_T_BTC), convert_dates=False).set_index('timestamp')
    btc_usdt_ps = FinancialInstrument("BTC/USDT", id="BTCUSDTPS", type=AssetType.PerpetualSwap)
    sol_usdt_ps = FinancialInstrument("SOL/USDT", id="SOLUSDTPS", type=AssetType.PerpetualSwap)
    db = CandleFeedDB()
    commission = MakerTakerCommission(maker_rate=0.001, taker_rate=0.002)
    db.add_kline(kline=btc_df, financial_type=btc_usdt_ps, timeframe=TimeframeType.H1, commission=commission)
    db.add_kline(kline=sol_df, financial_type=sol_usdt_ps, timeframe=TimeframeType.H1, commission=commission)
    proxy = CandleFeedProxy(db=db).set_position(sol_df.index[1])

    a = proxy.BTCUSDTPS_h1[-1]
    self.assertEqual(a.name, 1704067200000)