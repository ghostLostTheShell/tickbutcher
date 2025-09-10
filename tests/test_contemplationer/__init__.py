
from datetime import datetime
import unittest
from tickbutcher.brokers.common_broker import CommonBroker
from tickbutcher.candlefeed import TimeframeType
from tickbutcher.candlefeed.pandascandlefeed import PandasCandleFeed, load_dataframe_from_sql
from tickbutcher.commission import MakerTakerCommission
from tickbutcher.contemplationer import Contemplationer
from tickbutcher.products import AssetType, FinancialInstrument
from tickbutcher.brokers.trading_pair import common as common_trading_pair

class ContemplationerUnitTest(unittest.TestCase):
  def test_int_time_interval(self):
    self.assertEqual('yes', 'yes')
  
  def test_run(self):
    
    test_start_date = datetime.fromisoformat("2025-01-01T00:00:00+00:00:00")
    end_start_date = datetime.fromisoformat("2025-01-02T00:00:00+00:00:00")
    
    
    sol_usdt_1s_dataframe = load_dataframe_from_sql(inst_id='SOL/USDT', 
                                          timeframe='1s', 
                                          start_date=test_start_date, 
                                          end_date=end_start_date, 
                                          data_source_url="sqlite:///./tmp/app.db")
    
    _sol_usdt_ps = FinancialInstrument(symbol="SOL/USDT", type=AssetType.PerpetualSwap)

    sol_candle_feed = PandasCandleFeed(trading_pair=common_trading_pair.SOLUSDTP, 
                                       timeframe_level=TimeframeType.sec1,
                                       dataframe=sol_usdt_1s_dataframe)

    
    _maker_taker_commission = MakerTakerCommission(maker_rate=8, taker_rate=10)

    broker = CommonBroker()
    contemplationer = Contemplationer(timeframe_level=TimeframeType.sec1, brokers=[broker])
    contemplationer.add_kline(candleFeed=sol_candle_feed)


    contemplationer.run()
    
    self.assertEqual(contemplationer.current_time, sol_usdt_1s_dataframe.index[-1])
    
    