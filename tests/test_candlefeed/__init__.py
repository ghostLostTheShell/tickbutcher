from datetime import datetime
import unittest
from datetime import datetime, timedelta, timezone as TimeZone
from tickbutcher.candlefeed import TimeframeType
from tickbutcher.candlefeed.pandascandlefeed import load_dataframe_from_sql, PandasCandleFeed
from tickbutcher.products import AssetType, FinancialInstrument

class CandlefeedUnitTest(unittest.TestCase):
  
  def test_candle_feed_proxy(self):
    # sol_df = pd.read_json(StringIO(sol.USDT_T_SOL), convert_dates=False).set_index('timestamp')
    # btc_df = pd.read_json(StringIO(btc.USDT_T_BTC), convert_dates=False).set_index('timestamp')
    # btc_usdt_ps = FinancialInstrument("BTC/USDT", id="BTCUSDTPS", type=AssetType.PerpetualSwap)
    # sol_usdt_ps = FinancialInstrument("SOL/USDT", id="SOLUSDTPS", type=AssetType.PerpetualSwap)
    # db = CandleFeedDB()
    # commission = MakerTakerCommission(maker_rate=0.001, taker_rate=0.002)
    # db.add_kline(kline=btc_df, financial_type=btc_usdt_ps, timeframe=TimeframeType.H1, commission=commission)
    # db.add_kline(kline=sol_df, financial_type=sol_usdt_ps, timeframe=TimeframeType.H1, commission=commission)
    # proxy = CandleFeedProxy(db=db).set_position(sol_df.index[1])

    # a = proxy.BTCUSDTPS_h1[-1]
    # self.assertEqual(a.name, 1704067200000)
    pass  
  
  def test_klines_for_timeframe(self):
    """测试添加的k线数据的有效性"""
    test_start_date = datetime.fromisoformat("2025-01-01T00:00:00+00:00:00")
    end_start_date = datetime.fromisoformat("2025-01-10T00:00:00+00:00:00")

    # sol_usdt_1s = load_data_from_sql(inst_id='SOL/USDT', timeframe='1s', start_date=test_start_date, end_date=end_start_date, data_source_url="sqlite:///./tmp/app.db")
    # sol_usdt_1m = load_data_from_sql(inst_id='SOL/USDT', timeframe='1m', start_date=test_start_date, end_date=end_start_date, data_source_url="sqlite:///./tmp/app.db")

    # btc_usdt_ps = FinancialInstrument("BTC/USDT", id="BTCUSDTPS", type=AssetType.PerpetualSwap)
    # db = CandleFeedDB()
    
    # sol_usdt_ps = FinancialInstrument("SOL/USDT", id="SOLUSDTPS", type=AssetType.PerpetualSwap)
    # commission = MakerTakerCommission(maker_rate=0.001, taker_rate=0.002)
    # db.add_kline(kline=sol_usdt_1s, financial_type=sol_usdt_ps, timeframe=TimeframeType.S1, commission=commission)
    # db.add_kline(kline=sol_usdt_1m, financial_type=sol_usdt_ps, timeframe=TimeframeType.M1, commission=commission)
    
    # proxy = CandleFeedProxy(db=db).set_position(sol_usdt_1s.index[1])
    
    
    
    # a = proxy.SOLUSDTPS_s1[0]
    # b = proxy.SOLUSDTPS_m1[0]
    
  
    # print(a)
    
    # print(b)
    

class PandasCandleFeedUnitTest(unittest.TestCase):
  
  def test_load_data(self):
    """测试PandasCandleFeed的load_data方法"""
    test_start_date = datetime.fromisoformat("2025-01-02T00:00:00+00:00:00")
    end_start_date = datetime.fromisoformat("2025-01-10T00:00:00+00:00:00")
    
    
    sol_usdt_1s_dataframe = load_dataframe_from_sql(inst_id='SOL/USDT', 
                                          timeframe='1s', 
                                          start_date=test_start_date, 
                                          end_date=end_start_date, 
                                          data_source_url="sqlite:///./tmp/app.db")
    sol_usdt_1m = load_dataframe_from_sql(inst_id='SOL/USDT', 
                                          timeframe='1m', 
                                          start_date=test_start_date, 
                                          end_date=end_start_date, 
                                          data_source_url="sqlite:///./tmp/app.db")

    sol_usdt_ps = FinancialInstrument("SOL/USDT", id="SOLUSDTPS", type=AssetType.PerpetualSwap)

    # 检查PandasCandleFeed 对象的初始化时间
    start_time = datetime.now()
    sol_candle_feed = PandasCandleFeed(financial_type=sol_usdt_ps, 
                                       timeframe_level=TimeframeType.s1,
                                       dataframe=sol_usdt_1s_dataframe)
    sol_candle_feed.load_data(sol_usdt_1m, TimeframeType.min1)

    end_time = datetime.now()
    print(f"PandasCandleFeed initialized in {end_time - start_time}")


    indexs = sol_candle_feed.get_position_index_list()
    current_time = datetime.fromtimestamp(indexs[0]/1000, tz=TimeZone(timedelta(hours=0)))
    print(f"First index time: {current_time.isoformat()}")
    
    #测试秒级数据是否匹配
    sec = sol_candle_feed.s1(position=indexs[0])
    self.assertEqual(sec['volume'] , sol_usdt_1s_dataframe.loc[indexs[0], 'volume'])
    self.assertEqual(sec['open'], sol_usdt_1s_dataframe.loc[indexs[0], 'open'])
    self.assertEqual(sec['high'], sol_usdt_1s_dataframe.loc[indexs[0], 'high'])
    self.assertEqual(sec['low'], sol_usdt_1s_dataframe.loc[indexs[0], 'low'])
    self.assertEqual(sec['close'], sol_usdt_1s_dataframe.loc[indexs[0], 'close'])

    #测试秒级数据是否偏移是否正常
    sec_offset = sol_candle_feed.s1(position=indexs[0], offset=1)
    self.assertEqual(sec_offset['volume'], sol_usdt_1s_dataframe.loc[indexs[0] + 1000, 'volume'])
    self.assertEqual(sec_offset['open'], sol_usdt_1s_dataframe.loc[indexs[0] + 1000, 'open'])
    self.assertEqual(sec_offset['high'], sol_usdt_1s_dataframe.loc[indexs[0] + 1000, 'high'])
    self.assertEqual(sec_offset['low'], sol_usdt_1s_dataframe.loc[indexs[0] + 1000, 'low'])
    self.assertEqual(sec_offset['close'], sol_usdt_1s_dataframe.loc[indexs[0] + 1000, 'close'])

    #测试分钟级数据是否匹配
    min1 = sol_candle_feed.min1(position=indexs[0])
    self.assertEqual(min1['volume'], sol_usdt_1s_dataframe.loc[indexs[0], 'volume'])
    self.assertEqual(min1['open'], sol_usdt_1s_dataframe.loc[indexs[0], 'open'])
    self.assertEqual(min1['high'], sol_usdt_1s_dataframe.loc[indexs[0], 'high'])
    self.assertEqual(min1['low'], sol_usdt_1s_dataframe.loc[indexs[0], 'low'])
    self.assertEqual(min1['close'], sol_usdt_1s_dataframe.loc[indexs[0], 'close'])
    
    min1_sec05 = sol_candle_feed.min1(position=indexs[5])
    
    self.assertEqual(min1_sec05['volume'], sol_usdt_1s_dataframe.loc[indexs[0]:indexs[5], "volume"].sum())
    self.assertEqual(min1_sec05['open'], sol_usdt_1s_dataframe.loc[indexs[0], "open"])
    self.assertEqual(min1_sec05['high'], sol_usdt_1s_dataframe.loc[indexs[0]:indexs[5], "high"].max())
    self.assertEqual(min1_sec05['low'], sol_usdt_1s_dataframe.loc[indexs[0]:indexs[5], "low"].min())
    self.assertEqual(min1_sec05['close'], sol_usdt_1s_dataframe.loc[indexs[5], "close"])
    
    #测试分钟数据是否偏移是否正常
    
    

    pass
    