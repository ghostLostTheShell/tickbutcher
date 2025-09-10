from datetime import datetime
import unittest
from datetime import datetime, timedelta, timezone as TimeZone
from tickbutcher.brokers.trading_pair import common as common_trading_pair
from tests.dataset import get_sol_usdt_1s_and_1min
from tickbutcher.candlefeed import CandleIndexer, TimeframeType
from tickbutcher.candlefeed.pandascandlefeed import load_dataframe_from_sql, PandasCandleFeed

# 硬写入毫秒级时间戳时间间隔 1s | 1m | 5m | 15m | 1h | 4h | 1d | 1w | 1mo | 1y

# 硬写入可能导致日期天数不匹配，粗略把一月30天计算，一年365天计算

MILLISECONDS_IN_A_SECOND = 1000
MILLISECONDS_IN_A_MINUTE = MILLISECONDS_IN_A_SECOND * 60
MILLISECONDS_IN_AN_HOUR = MILLISECONDS_IN_A_MINUTE * 60
MILLISECONDS_IN_A_DAY = MILLISECONDS_IN_AN_HOUR * 24
MILLISECONDS_IN_A_WEEK = MILLISECONDS_IN_A_DAY * 7
MILLISECONDS_IN_A_MONTH = MILLISECONDS_IN_A_DAY * 30
MILLISECONDS_IN_A_YEAR = MILLISECONDS_IN_A_DAY * 365

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
sol_usdt_5m = load_dataframe_from_sql(inst_id='SOL/USDT',
                                      timeframe='5m',
                                      start_date=test_start_date,
                                      end_date=end_start_date,
                                      data_source_url="sqlite:///./tmp/app.db")
sol_usdt_15m = load_dataframe_from_sql(inst_id='SOL/USDT', 
                                      timeframe='15m', 
                                      start_date=test_start_date, 
                                      end_date=end_start_date, 
                                      data_source_url="sqlite:///./tmp/app.db")
sol_usdt_1h = load_dataframe_from_sql(inst_id='SOL/USDT', 
                                      timeframe='1h', 
                                      start_date=test_start_date, 
                                      end_date=end_start_date, 
                                      data_source_url="sqlite:///./tmp/app.db")
sol_usdt_4h = load_dataframe_from_sql(inst_id='SOL/USDT', 
                                      timeframe='4h', 
                                      start_date=test_start_date, 
                                      end_date=end_start_date, 
                                      data_source_url="sqlite:///./tmp/app.db")
sol_usdt_1d = load_dataframe_from_sql(inst_id='SOL/USDT', 
                                      timeframe='1d', 
                                      start_date=test_start_date, 
                                      end_date=end_start_date, 
                                      data_source_url="sqlite:///./tmp/app.db")
sol_usdt_1w = load_dataframe_from_sql(inst_id='SOL/USDT', 
                                      timeframe='1w', 
                                      start_date=test_start_date, 
                                      end_date=end_start_date, 
                                      data_source_url="sqlite:///./tmp/app.db")
sol_usdt_1mo = load_dataframe_from_sql(inst_id='SOL/USDT', 
                                      timeframe='1mo', 
                                      start_date=test_start_date, 
                                      end_date=end_start_date, 
                                      data_source_url="sqlite:///./tmp/app.db")

class CandlefeedUnitTest(unittest.TestCase):
  
  def test_candle_indexer(self):
    solusdt_1s, solusdt_1min= get_sol_usdt_1s_and_1min()

    sol_candle_feed = PandasCandleFeed(trading_pair=common_trading_pair.SOLUSDTP,
                                       timeframe_level=TimeframeType.sec1,
                                       dataframe=solusdt_1s)
    sol_candle_feed.load_data(solusdt_1min, TimeframeType.min1)
    indexs = sol_candle_feed.get_position_index_list()
    
    candle_indexer = CandleIndexer(position=indexs[0], 
                                   table={common_trading_pair.SOLUSDTP: sol_candle_feed},
                                   min_time_frame=TimeframeType.sec1)

    sec = candle_indexer.SOLUSDTP_sec1[0]
    self.assertEqual(sec['volume'], solusdt_1s.loc[indexs[0], 'volume'])
    self.assertEqual(sec['open'], solusdt_1s.loc[indexs[0], 'open'])
    self.assertEqual(sec['high'], solusdt_1s.loc[indexs[0], 'high'])
    self.assertEqual(sec['low'], solusdt_1s.loc[indexs[0], 'low'])
    self.assertEqual(sec['close'], solusdt_1s.loc[indexs[0], 'close'])
    
    #测试不带时间框架
    sec = candle_indexer.SOLUSDTP[0]
    self.assertEqual(sec['volume'], solusdt_1s.loc[indexs[0], 'volume'])
    self.assertEqual(sec['open'], solusdt_1s.loc[indexs[0], 'open'])
    self.assertEqual(sec['high'], solusdt_1s.loc[indexs[0], 'high'])
    self.assertEqual(sec['low'], solusdt_1s.loc[indexs[0], 'low'])
    self.assertEqual(sec['close'], solusdt_1s.loc[indexs[0], 'close'])
    
  
  def test_klines_for_timeframe(self):
    """测试添加的k线数据的有效性"""
    _test_start_date = datetime.fromisoformat("2025-01-01T00:00:00+00:00:00")
    _end_start_date = datetime.fromisoformat("2025-01-10T00:00:00+00:00:00")

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

  def test_load_data_on_level_sec1(self):
    """测试PandasCandleFeed的load_data方法"""


    # 检查PandasCandleFeed 对象的初始化时间
    start_time = datetime.now()
    sol_candle_feed = PandasCandleFeed(trading_pair=common_trading_pair.SOLUSDTP,
                                       timeframe_level=TimeframeType.sec1,
                                       dataframe=sol_usdt_1s_dataframe)
    sol_candle_feed.load_data(sol_usdt_1m, TimeframeType.min1)
    sol_candle_feed.load_data(sol_usdt_5m, TimeframeType.min5)
    sol_candle_feed.load_data(sol_usdt_15m, TimeframeType.min15)
    sol_candle_feed.load_data(sol_usdt_1h, TimeframeType.h1)
    sol_candle_feed.load_data(sol_usdt_4h, TimeframeType.h4)
    sol_candle_feed.load_data(sol_usdt_1d, TimeframeType.d1)
    sol_candle_feed.load_data(sol_usdt_1w, TimeframeType.w1)
    sol_candle_feed.load_data(sol_usdt_1mo, TimeframeType.mo1)

    end_time = datetime.now()
    print(f"PandasCandleFeed initialized in {end_time - start_time}")


    indexs = sol_candle_feed.get_position_index_list()
    current_time = datetime.fromtimestamp(indexs[0]/1000, tz=TimeZone(timedelta(hours=0)))
    print(f"First index time: {current_time.isoformat()}")
    
    #测试秒级数据是否匹配
    sec = sol_candle_feed.sec1(position=indexs[0])
    self.assertEqual(sec['volume'] , sol_usdt_1s_dataframe.loc[indexs[0], 'volume'])
    self.assertEqual(sec['open'], sol_usdt_1s_dataframe.loc[indexs[0], 'open'])
    self.assertEqual(sec['high'], sol_usdt_1s_dataframe.loc[indexs[0], 'high'])
    self.assertEqual(sec['low'], sol_usdt_1s_dataframe.loc[indexs[0], 'low'])
    self.assertEqual(sec['close'], sol_usdt_1s_dataframe.loc[indexs[0], 'close'])

    #测试秒级数据是否偏移是否正常
    sec_offset = sol_candle_feed.sec1(position=indexs[0], offset=1)
    self.assertEqual(sec_offset['volume'], sol_usdt_1s_dataframe.loc[indexs[0] + MILLISECONDS_IN_A_SECOND, 'volume'])
    self.assertEqual(sec_offset['open'], sol_usdt_1s_dataframe.loc[indexs[0] + MILLISECONDS_IN_A_SECOND, 'open'])
    self.assertEqual(sec_offset['high'], sol_usdt_1s_dataframe.loc[indexs[0] + MILLISECONDS_IN_A_SECOND, 'high'])
    self.assertEqual(sec_offset['low'], sol_usdt_1s_dataframe.loc[indexs[0] + MILLISECONDS_IN_A_SECOND, 'low'])
    self.assertEqual(sec_offset['close'], sol_usdt_1s_dataframe.loc[indexs[0] + MILLISECONDS_IN_A_SECOND, 'close'])


    # 注意，以下测试用例测试“匹配”是基于秒级匹配，如果不是完整的间隔会自动从大时间间隔递归到秒

    # 测试“偏移”由于手动定义了偏移量offset，根据定义不会执行向下递归，而是在相同时间间隔的数据中计算偏移

    # 注意，周、月级别的数据由于时间间隔较大，可能无法在测试数据中找到匹配的时间戳，因此这些测试用例可能会失败

    #测试分钟级数据是否匹配
    min1 = sol_candle_feed.min1(position=indexs[0])
    self.assertEqual(min1['volume'], sol_usdt_1s_dataframe.loc[indexs[0], 'volume'])
    self.assertEqual(min1['open'], sol_usdt_1s_dataframe.loc[indexs[0], 'open'])
    self.assertEqual(min1['high'], sol_usdt_1s_dataframe.loc[indexs[0], 'high'])
    self.assertEqual(min1['low'], sol_usdt_1s_dataframe.loc[indexs[0], 'low'])
    self.assertEqual(min1['close'], sol_usdt_1s_dataframe.loc[indexs[0], 'close'])

    #测试分钟数据与秒级的聚合是否正确
    min1_sec05 = sol_candle_feed.min1(position=indexs[5])
    
    self.assertEqual(min1_sec05['volume'], sol_usdt_1s_dataframe.loc[indexs[0]:indexs[5], "volume"].sum())
    self.assertEqual(min1_sec05['open'], sol_usdt_1s_dataframe.loc[indexs[0], "open"])
    self.assertEqual(min1_sec05['high'], sol_usdt_1s_dataframe.loc[indexs[0]:indexs[5], "high"].max())
    self.assertEqual(min1_sec05['low'], sol_usdt_1s_dataframe.loc[indexs[0]:indexs[5], "low"].min())
    self.assertEqual(min1_sec05['close'], sol_usdt_1s_dataframe.loc[indexs[5], "close"])
    
    #测试分钟数据是否偏移是否正常
    min1_offset = sol_candle_feed.min1(position=indexs[0], offset=1)
    self.assertEqual(min1_offset['volume'], sol_usdt_1m.loc[indexs[0] + MILLISECONDS_IN_A_MINUTE, 'volume'])
    self.assertEqual(min1_offset['open'], sol_usdt_1m.loc[indexs[0] + MILLISECONDS_IN_A_MINUTE, 'open'])
    self.assertEqual(min1_offset['high'], sol_usdt_1m.loc[indexs[0] + MILLISECONDS_IN_A_MINUTE, 'high'])
    self.assertEqual(min1_offset['low'], sol_usdt_1m.loc[indexs[0] + MILLISECONDS_IN_A_MINUTE, 'low'])
    self.assertEqual(min1_offset['close'], sol_usdt_1m.loc[indexs[0] + MILLISECONDS_IN_A_MINUTE, 'close'])

    #测试5分钟数据是否匹配
    min5 = sol_candle_feed.min5(position=indexs[0])
    self.assertEqual(min5['volume'], sol_usdt_1s_dataframe.loc[indexs[0], 'volume'])
    self.assertEqual(min5['open'], sol_usdt_1s_dataframe.loc[indexs[0], 'open'])
    self.assertEqual(min5['high'], sol_usdt_1s_dataframe.loc[indexs[0], 'high'])
    self.assertEqual(min5['low'], sol_usdt_1s_dataframe.loc[indexs[0], 'low'])
    self.assertEqual(min5['close'], sol_usdt_1s_dataframe.loc[indexs[0], 'close'])

    #测试5分钟数据是否偏移是否正常
    min5_offset = sol_candle_feed.min5(position=indexs[0], offset=1)
    self.assertEqual(min5_offset['volume'], sol_usdt_5m.loc[indexs[0] + MILLISECONDS_IN_A_MINUTE * 5, 'volume'])
    self.assertEqual(min5_offset['open'], sol_usdt_5m.loc[indexs[0] + MILLISECONDS_IN_A_MINUTE * 5, 'open'])
    self.assertEqual(min5_offset['high'], sol_usdt_5m.loc[indexs[0] + MILLISECONDS_IN_A_MINUTE * 5, 'high'])
    self.assertEqual(min5_offset['low'], sol_usdt_5m.loc[indexs[0] + MILLISECONDS_IN_A_MINUTE * 5, 'low'])
    self.assertEqual(min5_offset['close'], sol_usdt_5m.loc[indexs[0] + MILLISECONDS_IN_A_MINUTE * 5, 'close'])

    #测试15分钟数据是否匹配
    min15 = sol_candle_feed.min15(position=indexs[0])
    self.assertEqual(min15['volume'], sol_usdt_1s_dataframe.loc[indexs[0], 'volume'])
    self.assertEqual(min15['open'], sol_usdt_1s_dataframe.loc[indexs[0], 'open'])
    self.assertEqual(min15['high'], sol_usdt_1s_dataframe.loc[indexs[0], 'high'])
    self.assertEqual(min15['low'], sol_usdt_1s_dataframe.loc[indexs[0], 'low'])
    self.assertEqual(min15['close'], sol_usdt_1s_dataframe.loc[indexs[0], 'close'])

    #测试15分钟数据是否偏移是否正常
    min15_offset = sol_candle_feed.min15(position=indexs[0], offset=1)
    self.assertEqual(min15_offset['volume'], sol_usdt_15m.loc[indexs[0] + MILLISECONDS_IN_A_MINUTE * 15, 'volume'])
    self.assertEqual(min15_offset['open'], sol_usdt_15m.loc[indexs[0] + MILLISECONDS_IN_A_MINUTE * 15, 'open'])
    self.assertEqual(min15_offset['high'], sol_usdt_15m.loc[indexs[0] + MILLISECONDS_IN_A_MINUTE * 15, 'high'])
    self.assertEqual(min15_offset['low'], sol_usdt_15m.loc[indexs[0] + MILLISECONDS_IN_A_MINUTE * 15, 'low'])
    self.assertEqual(min15_offset['close'], sol_usdt_15m.loc[indexs[0] + MILLISECONDS_IN_A_MINUTE * 15, 'close'])

    #测试1小时数据是否匹配
    h1 = sol_candle_feed.h1(position=indexs[0])
    self.assertEqual(h1['volume'], sol_usdt_1s_dataframe.loc[indexs[0], 'volume'])
    self.assertEqual(h1['open'], sol_usdt_1s_dataframe.loc[indexs[0], 'open'])
    self.assertEqual(h1['high'], sol_usdt_1s_dataframe.loc[indexs[0], 'high'])
    self.assertEqual(h1['low'], sol_usdt_1s_dataframe.loc[indexs[0], 'low'])
    self.assertEqual(h1['close'], sol_usdt_1s_dataframe.loc[indexs[0], 'close'])

    #测试1小时数据是否偏移是否正常
    h1_offset = sol_candle_feed.h1(position=indexs[0], offset=1)
    self.assertEqual(h1_offset['volume'], sol_usdt_1h.loc[indexs[0] + MILLISECONDS_IN_AN_HOUR, 'volume'])
    self.assertEqual(h1_offset['open'], sol_usdt_1h.loc[indexs[0] + MILLISECONDS_IN_AN_HOUR, 'open'])
    self.assertEqual(h1_offset['high'], sol_usdt_1h.loc[indexs[0] + MILLISECONDS_IN_AN_HOUR, 'high'])
    self.assertEqual(h1_offset['low'], sol_usdt_1h.loc[indexs[0] + MILLISECONDS_IN_AN_HOUR, 'low'])
    self.assertEqual(h1_offset['close'], sol_usdt_1h.loc[indexs[0] + MILLISECONDS_IN_AN_HOUR, 'close'])

    #测试4小时数据是否匹配
    h4 = sol_candle_feed.h4(position=indexs[0])
    self.assertEqual(h4['volume'], sol_usdt_1s_dataframe.loc[indexs[0], 'volume'])
    self.assertEqual(h4['open'], sol_usdt_1s_dataframe.loc[indexs[0], 'open'])
    self.assertEqual(h4['high'], sol_usdt_1s_dataframe.loc[indexs[0], 'high'])
    self.assertEqual(h4['low'], sol_usdt_1s_dataframe.loc[indexs[0], 'low'])
    self.assertEqual(h4['close'], sol_usdt_1s_dataframe.loc[indexs[0], 'close'])

    #测试4小时数据是否偏移是否正常
    h4_offset = sol_candle_feed.h4(position=indexs[0], offset=1)
    self.assertEqual(h4_offset['volume'], sol_usdt_4h.loc[indexs[0] + MILLISECONDS_IN_AN_HOUR * 4, 'volume'])
    self.assertEqual(h4_offset['open'], sol_usdt_4h.loc[indexs[0] + MILLISECONDS_IN_AN_HOUR * 4, 'open'])
    self.assertEqual(h4_offset['high'], sol_usdt_4h.loc[indexs[0] + MILLISECONDS_IN_AN_HOUR * 4, 'high'])
    self.assertEqual(h4_offset['low'], sol_usdt_4h.loc[indexs[0] + MILLISECONDS_IN_AN_HOUR * 4, 'low'])
    self.assertEqual(h4_offset['close'], sol_usdt_4h.loc[indexs[0] + MILLISECONDS_IN_AN_HOUR * 4, 'close'])

    #测试1天数据是否匹配
    d1 = sol_candle_feed.d1(position=indexs[0])
    self.assertEqual(d1['volume'], sol_usdt_1s_dataframe.loc[indexs[0], 'volume'])
    self.assertEqual(d1['open'], sol_usdt_1s_dataframe.loc[indexs[0], 'open'])
    self.assertEqual(d1['high'], sol_usdt_1s_dataframe.loc[indexs[0], 'high'])
    self.assertEqual(d1['low'], sol_usdt_1s_dataframe.loc[indexs[0], 'low'])
    self.assertEqual(d1['close'], sol_usdt_1s_dataframe.loc[indexs[0], 'close'])

    #测试1天数据是否偏移是否正常
    d1_offset = sol_candle_feed.d1(position=indexs[0], offset=1)
    self.assertEqual(d1_offset['volume'], sol_usdt_1d.loc[indexs[0] + MILLISECONDS_IN_A_DAY, 'volume'])
    self.assertEqual(d1_offset['open'], sol_usdt_1d.loc[indexs[0] + MILLISECONDS_IN_A_DAY, 'open'])
    self.assertEqual(d1_offset['high'], sol_usdt_1d.loc[indexs[0] + MILLISECONDS_IN_A_DAY, 'high'])
    self.assertEqual(d1_offset['low'], sol_usdt_1d.loc[indexs[0] + MILLISECONDS_IN_A_DAY, 'low'])
    self.assertEqual(d1_offset['close'], sol_usdt_1d.loc[indexs[0] + MILLISECONDS_IN_A_DAY, 'close'])

    # #测试1周数据是否匹配
    # w1 = sol_candle_feed.w1(position=indexs[0])
    # self.assertEqual(w1['volume'], sol_usdt_1s_dataframe.loc[indexs[0], 'volume'])
    # self.assertEqual(w1['open'], sol_usdt_1s_dataframe.loc[indexs[0], 'open'])
    # self.assertEqual(w1['high'], sol_usdt_1s_dataframe.loc[indexs[0], 'high'])
    # self.assertEqual(w1['low'], sol_usdt_1s_dataframe.loc[indexs[0], 'low'])
    # self.assertEqual(w1['close'], sol_usdt_1s_dataframe.loc[indexs[0], 'close'])

    # #测试1周数据是否偏移是否正常
    # w1_offset = sol_candle_feed.w1(position=indexs[0], offset=1)
    # self.assertEqual(w1_offset['volume'], sol_usdt_1w.loc[indexs[0] + MILLISECONDS_IN_A_WEEK, 'volume'])
    # self.assertEqual(w1_offset['open'], sol_usdt_1w.loc[indexs[0] + MILLISECONDS_IN_A_WEEK, 'open'])
    # self.assertEqual(w1_offset['high'], sol_usdt_1w.loc[indexs[0] + MILLISECONDS_IN_A_WEEK, 'high'])
    # self.assertEqual(w1_offset['low'], sol_usdt_1w.loc[indexs[0] + MILLISECONDS_IN_A_WEEK, 'low'])
    # self.assertEqual(w1_offset['close'], sol_usdt_1w.loc[indexs[0] + MILLISECONDS_IN_A_WEEK, 'close'])

    # #测试1月数据是否匹配
    # mo1 = sol_candle_feed.mo1(position=indexs[0])
    # self.assertEqual(mo1['volume'], sol_usdt_1s_dataframe.loc[indexs[0], 'volume'])
    # self.assertEqual(mo1['open'], sol_usdt_1s_dataframe.loc[indexs[0], 'open'])
    # self.assertEqual(mo1['high'], sol_usdt_1s_dataframe.loc[indexs[0], 'high'])
    # self.assertEqual(mo1['low'], sol_usdt_1s_dataframe.loc[indexs[0], 'low'])
    # self.assertEqual(mo1['close'], sol_usdt_1s_dataframe.loc[indexs[0], 'close'])

    # #测试1月数据是否偏移是否正常
    # mo1_offset = sol_candle_feed.mo1(position=indexs[0], offset=1)
    # self.assertEqual(mo1_offset['volume'], sol_usdt_1mo.loc[indexs[0] + MILLISECONDS_IN_A_MONTH, 'volume'])
    # self.assertEqual(mo1_offset['open'], sol_usdt_1mo.loc[indexs[0] + MILLISECONDS_IN_A_MONTH, 'open'])
    # self.assertEqual(mo1_offset['high'], sol_usdt_1mo.loc[indexs[0] + MILLISECONDS_IN_A_MONTH, 'high'])
    # self.assertEqual(mo1_offset['low'], sol_usdt_1mo.loc[indexs[0] + MILLISECONDS_IN_A_MONTH, 'low'])
    # self.assertEqual(mo1_offset['close'], sol_usdt_1mo.loc[indexs[0] + MILLISECONDS_IN_A_MONTH, 'close'])

  def test_load_data_on_level_min1(self):
    """测试最小时间粒度为1分钟，聚合与偏移是否正确"""
    # 以1分钟为最小粒度初始化
    candle_feed = PandasCandleFeed(trading_pair=common_trading_pair.SOLUSDTP,
                                   timeframe_level=TimeframeType.min1,
                                   dataframe=sol_usdt_1m)
    # 加载更大时间粒度数据
    candle_feed.load_data(sol_usdt_5m, TimeframeType.min5)
    candle_feed.load_data(sol_usdt_15m, TimeframeType.min15)
    candle_feed.load_data(sol_usdt_1h, TimeframeType.h1)
    candle_feed.load_data(sol_usdt_4h, TimeframeType.h4)
    candle_feed.load_data(sol_usdt_1d, TimeframeType.d1)
    indexs = candle_feed.get_position_index_list()
    base_pos = indexs[0]
    # 1分钟级直接匹配
    m1 = candle_feed.min1(position=base_pos)
    self.assertEqual(m1['open'], sol_usdt_1m.loc[base_pos, 'open'])
    self.assertEqual(m1['close'], sol_usdt_1m.loc[base_pos, 'close'])
    # 5分钟聚合，当前位置不足完整5分钟则应该等于起始1分钟k线
    m5 = candle_feed.min5(position=base_pos)
    self.assertEqual(m5['open'], sol_usdt_1m.loc[base_pos, 'open'])
    # 5分钟偏移一段
    m5_offset = candle_feed.min5(position=base_pos, offset=1)
    off5 = base_pos + MILLISECONDS_IN_A_MINUTE * 5
    self.assertEqual(m5_offset['open'], sol_usdt_5m.loc[off5, 'open'])
    # 15分钟
    m15 = candle_feed.min15(position=base_pos)
    self.assertEqual(m15['open'], sol_usdt_1m.loc[base_pos, 'open'])
    m15_offset = candle_feed.min15(position=base_pos, offset=1)
    off15 = base_pos + MILLISECONDS_IN_A_MINUTE * 15
    self.assertEqual(m15_offset['open'], sol_usdt_15m.loc[off15, 'open'])
    # 1小时
    h1 = candle_feed.h1(position=base_pos)
    self.assertEqual(h1['open'], sol_usdt_1m.loc[base_pos, 'open'])
    h1_offset = candle_feed.h1(position=base_pos, offset=1)
    offh1 = base_pos + MILLISECONDS_IN_AN_HOUR
    self.assertEqual(h1_offset['open'], sol_usdt_1h.loc[offh1, 'open'])
    # 4小时
    h4 = candle_feed.h4(position=base_pos)
    self.assertEqual(h4['open'], sol_usdt_1m.loc[base_pos, 'open'])
    h4_offset = candle_feed.h4(position=base_pos, offset=1)
    offh4 = base_pos + MILLISECONDS_IN_AN_HOUR * 4
    self.assertEqual(h4_offset['open'], sol_usdt_4h.loc[offh4, 'open'])
    # 1天
    d1 = candle_feed.d1(position=base_pos)
    self.assertEqual(d1['open'], sol_usdt_1m.loc[base_pos, 'open'])
    d1_offset = candle_feed.d1(position=base_pos, offset=1)
    offd1 = base_pos + MILLISECONDS_IN_A_DAY
    self.assertEqual(d1_offset['open'], sol_usdt_1d.loc[offd1, 'open'])

  def test_load_data_on_level_min5(self):
    """测试最小时间粒度为5分钟"""
    candle_feed = PandasCandleFeed(trading_pair=common_trading_pair.SOLUSDTP,
                                   timeframe_level=TimeframeType.min5,
                                   dataframe=sol_usdt_5m)
    candle_feed.load_data(sol_usdt_15m, TimeframeType.min15)
    candle_feed.load_data(sol_usdt_1h, TimeframeType.h1)
    candle_feed.load_data(sol_usdt_4h, TimeframeType.h4)
    candle_feed.load_data(sol_usdt_1d, TimeframeType.d1)
    indexs = candle_feed.get_position_index_list()
    base_pos = indexs[0]
    # 5分钟直接匹配
    m5 = candle_feed.min5(position=base_pos)
    for col in ['open','high','low','close','volume']:
      self.assertEqual(m5[col], sol_usdt_5m.loc[base_pos, col])
    # 5分钟偏移
    m5_offset = candle_feed.min5(position=base_pos, offset=1)
    off5 = base_pos + MILLISECONDS_IN_A_MINUTE * 5
    for col in ['open','high','low','close','volume']:
      self.assertEqual(m5_offset[col], sol_usdt_5m.loc[off5, col])
    # 15分钟聚合
    m15 = candle_feed.min15(position=base_pos)
    self.assertEqual(m15['open'], sol_usdt_5m.loc[base_pos, 'open'])
    # 15分钟偏移
    m15_offset = candle_feed.min15(position=base_pos, offset=1)
    off15 = base_pos + MILLISECONDS_IN_A_MINUTE * 15
    self.assertEqual(m15_offset['open'], sol_usdt_15m.loc[off15, 'open'])
    # 1小时
    h1 = candle_feed.h1(position=base_pos)
    self.assertEqual(h1['open'], sol_usdt_5m.loc[base_pos, 'open'])
    h1_offset = candle_feed.h1(position=base_pos, offset=1)
    offh1 = base_pos + MILLISECONDS_IN_AN_HOUR
    self.assertEqual(h1_offset['open'], sol_usdt_1h.loc[offh1, 'open'])
    # 4小时
    h4 = candle_feed.h4(position=base_pos)
    self.assertEqual(h4['open'], sol_usdt_5m.loc[base_pos, 'open'])
    h4_offset = candle_feed.h4(position=base_pos, offset=1)
    offh4 = base_pos + MILLISECONDS_IN_AN_HOUR * 4
    self.assertEqual(h4_offset['open'], sol_usdt_4h.loc[offh4, 'open'])
    # 1天
    d1 = candle_feed.d1(position=base_pos)
    self.assertEqual(d1['open'], sol_usdt_5m.loc[base_pos, 'open'])
    d1_offset = candle_feed.d1(position=base_pos, offset=1)
    offd1 = base_pos + MILLISECONDS_IN_A_DAY
    self.assertEqual(d1_offset['open'], sol_usdt_1d.loc[offd1, 'open'])

  def test_load_data_on_level_min15(self):
    """测试最小时间粒度为15分钟"""
    candle_feed = PandasCandleFeed(trading_pair=common_trading_pair.SOLUSDTP,
                                   timeframe_level=TimeframeType.min15,
                                   dataframe=sol_usdt_15m)
    candle_feed.load_data(sol_usdt_1h, TimeframeType.h1)
    candle_feed.load_data(sol_usdt_4h, TimeframeType.h4)
    candle_feed.load_data(sol_usdt_1d, TimeframeType.d1)
    indexs = candle_feed.get_position_index_list()
    base_pos = indexs[0]
    # 15分钟匹配
    m15 = candle_feed.min15(position=base_pos)
    self.assertEqual(m15['open'], sol_usdt_15m.loc[base_pos, 'open'])
    # 15分钟偏移
    m15_offset = candle_feed.min15(position=base_pos, offset=1)
    off15 = base_pos + MILLISECONDS_IN_A_MINUTE * 15
    self.assertEqual(m15_offset['open'], sol_usdt_15m.loc[off15, 'open'])
    # 1小时
    h1 = candle_feed.h1(position=base_pos)
    self.assertEqual(h1['open'], sol_usdt_15m.loc[base_pos, 'open'])
    h1_offset = candle_feed.h1(position=base_pos, offset=1)
    offh1 = base_pos + MILLISECONDS_IN_AN_HOUR
    self.assertEqual(h1_offset['open'], sol_usdt_1h.loc[offh1, 'open'])
    # 4小时
    h4 = candle_feed.h4(position=base_pos)
    self.assertEqual(h4['open'], sol_usdt_15m.loc[base_pos, 'open'])
    h4_offset = candle_feed.h4(position=base_pos, offset=1)
    offh4 = base_pos + MILLISECONDS_IN_AN_HOUR * 4
    self.assertEqual(h4_offset['open'], sol_usdt_4h.loc[offh4, 'open'])
    # 1天
    d1 = candle_feed.d1(position=base_pos)
    self.assertEqual(d1['open'], sol_usdt_15m.loc[base_pos, 'open'])
    d1_offset = candle_feed.d1(position=base_pos, offset=1)
    offd1 = base_pos + MILLISECONDS_IN_A_DAY
    self.assertEqual(d1_offset['open'], sol_usdt_1d.loc[offd1, 'open'])

  def test_load_data_on_level_hour1(self):
    """测试最小时间粒度为1小时"""
    candle_feed = PandasCandleFeed(trading_pair=common_trading_pair.SOLUSDTP,
                                   timeframe_level=TimeframeType.h1,
                                   dataframe=sol_usdt_1h)
    candle_feed.load_data(sol_usdt_4h, TimeframeType.h4)
    candle_feed.load_data(sol_usdt_1d, TimeframeType.d1)
    indexs = candle_feed.get_position_index_list()
    base_pos = indexs[0]
    # 1小时匹配
    h1 = candle_feed.h1(position=base_pos)
    self.assertEqual(h1['open'], sol_usdt_1h.loc[base_pos, 'open'])
    # 1小时偏移
    h1_offset = candle_feed.h1(position=base_pos, offset=1)
    offh1 = base_pos + MILLISECONDS_IN_AN_HOUR
    self.assertEqual(h1_offset['open'], sol_usdt_1h.loc[offh1, 'open'])
    # 4小时
    h4 = candle_feed.h4(position=base_pos)
    self.assertEqual(h4['open'], sol_usdt_1h.loc[base_pos, 'open'])
    h4_offset = candle_feed.h4(position=base_pos, offset=1)
    offh4 = base_pos + MILLISECONDS_IN_AN_HOUR * 4
    self.assertEqual(h4_offset['open'], sol_usdt_4h.loc[offh4, 'open'])
    # 1天
    d1 = candle_feed.d1(position=base_pos)
    self.assertEqual(d1['open'], sol_usdt_1h.loc[base_pos, 'open'])
    d1_offset = candle_feed.d1(position=base_pos, offset=1)
    offd1 = base_pos + MILLISECONDS_IN_A_DAY
    self.assertEqual(d1_offset['open'], sol_usdt_1d.loc[offd1, 'open'])

  def test_load_data_on_level_hour4(self):
    """测试最小时间粒度为4小时"""
    candle_feed = PandasCandleFeed(trading_pair=common_trading_pair.SOLUSDTP,
                                   timeframe_level=TimeframeType.h4,
                                   dataframe=sol_usdt_4h)
    candle_feed.load_data(sol_usdt_1d, TimeframeType.d1)
    indexs = candle_feed.get_position_index_list()
    base_pos = indexs[0]
    # 4小时匹配
    h4 = candle_feed.h4(position=base_pos)
    self.assertEqual(h4['open'], sol_usdt_4h.loc[base_pos, 'open'])
    # 4小时偏移
    h4_offset = candle_feed.h4(position=base_pos, offset=1)
    offh4 = base_pos + MILLISECONDS_IN_AN_HOUR * 4
    self.assertEqual(h4_offset['open'], sol_usdt_4h.loc[offh4, 'open'])
    # 1天
    d1 = candle_feed.d1(position=base_pos)
    self.assertEqual(d1['open'], sol_usdt_4h.loc[base_pos, 'open'])
    d1_offset = candle_feed.d1(position=base_pos, offset=1)
    offd1 = base_pos + MILLISECONDS_IN_A_DAY
    self.assertEqual(d1_offset['open'], sol_usdt_1d.loc[offd1, 'open'])

  def test_load_data_on_level_day1(self):
    """测试最小时间粒度为1天"""
    candle_feed = PandasCandleFeed(trading_pair=common_trading_pair.SOLUSDTP,
                                   timeframe_level=TimeframeType.d1,
                                   dataframe=sol_usdt_1d)
    indexs = candle_feed.get_position_index_list()
    base_pos = indexs[0]
    # 1天匹配
    d1 = candle_feed.d1(position=base_pos)
    self.assertEqual(d1['open'], sol_usdt_1d.loc[base_pos, 'open'])
    # 1天偏移
    d1_offset = candle_feed.d1(position=base_pos, offset=1)
    offd1 = base_pos + MILLISECONDS_IN_A_DAY
    self.assertEqual(d1_offset['open'], sol_usdt_1d.loc[offd1, 'open'])


    
    
if __name__ == '__main__':
  unittest.main()