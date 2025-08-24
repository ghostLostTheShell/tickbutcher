from io import StringIO
import unittest

import pandas as pd
from tickbutcher.candlefeed import TimeframeType
from tickbutcher.commission import MakerTakerCommission
from tickbutcher.contemplationer import Contemplationer
from tickbutcher.products import AssetType, FinancialInstrument
from ..dataset import sol,btc

class ContemplationerUnitTest(unittest.TestCase):
  def test_int_time_interval(self):
    
    sol_df = pd.read_json(StringIO(sol.USDT_T_SOL), convert_dates=False).set_index('timestamp')
    btc_df = pd.read_json(StringIO(btc.USDT_T_BTC), convert_dates=False).set_index('timestamp')
    
    print(sol_df)
    # print(df.index)          # 显示索引对象
    # print(df.index.dtype)    # 查看索引里元素的数据类型
    # print(type(df.index))    # 查看索引对象的类型

    new_index = sol_df.index.union(btc_df.index)
    print(new_index)
    new_index = sol_df.index.union(btc_df.index)
    print(f"New index size: {new_index.size}, new_index[0] {new_index[0]}")

    for time in new_index:
        print(f"\n\nTime: {time}")        
        print(f"\nsol_df.loc[time]: {sol_df.loc[time] if time in sol_df.index else None}\n pos[{sol_df.index.get_loc(time)}]")
        # print(f"\nbtc_df.loc[time]: {btc_df.loc[time] if time in btc_df.index else None}\n pos[{btc_df.index.get_loc(time)}]")

    Contemplationer()
    self.assertEqual('yes', 'yes')
  
  def test_run(self):
    sol_df = pd.read_json(StringIO(sol.USDT_T_SOL), convert_dates=False).set_index('timestamp')
    btc_df = pd.read_json(StringIO(btc.USDT_T_BTC), convert_dates=False).set_index('timestamp')
    
    commission = MakerTakerCommission(maker_rate=0.001, taker_rate=0.002)
    contemplationer = Contemplationer()
    btc_usdt_ps = FinancialInstrument("BTC/USDT", id="BTC_USDT_PS", type=AssetType.PerpetualSwap)
    contemplationer.add_kline(kline=btc_df, financial_type=btc_usdt_ps, timeframe=TimeframeType.H1, commission=commission)

    sol_usdt_ps = FinancialInstrument("SOL/USDT", id="SOL_USDT_PS", type=AssetType.PerpetualSwap)
    contemplationer.add_kline(kline=sol_df, financial_type=sol_usdt_ps, timeframe=TimeframeType.H1, commission=commission)

    contemplationer.run()
    
    