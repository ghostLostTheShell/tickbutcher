
import unittest
from tests.dataset import get_sol_usdt_1s_and_1min
from tickbutcher.alphahub import AlphaHub
from tickbutcher.brokers.common_broker import CommonBroker
from tickbutcher.candlefeed import TimeframeType
from tickbutcher.candlefeed.pandascandlefeed import PandasCandleFeed
from tickbutcher.brokers.trading_pair import common as common_trading_pair
from tickbutcher.log import logger
from tickbutcher.order import OrderType
from tickbutcher.strategys.common_strategy import CommonStrategy
from tickbutcher.Indicators.mfi import MoneyFlowIndex
from tickbutcher.products import common as common_product

class TestStrategy(CommonStrategy):
  
  def next(self):
    mfi = self.alpha_hub.get_indicator('mfi', MoneyFlowIndex) 
    mfi_result = mfi.get_curret_result(common_trading_pair.SOLUSDT)
    solusdt = self.candled.SOLUSDT
    if mfi_result is None:
      return
    else:
      if mfi_result.signal_strength > 0.5 and mfi_result.signal_strength < 0.8:
        logger.info(f"{solusdt.get_iso_datetime()}:: {solusdt[0]} :: mfi:: {mfi_result.value} -- 买入信号")
        self.long_entry(trading_pair=common_trading_pair.SOLUSDT,
          quantity=0.1,
          order_type=OrderType.Market)
        
      elif mfi_result.signal_strength <= -0.5 and mfi_result.signal_strength > -0.7:
        logger.info(f"{solusdt.get_iso_datetime()}:: {solusdt[0]} :: mfi:: {mfi_result.value} -- 卖出信号")
      elif mfi_result.signal_strength >= 0.9:
        logger.info(f"{solusdt.get_iso_datetime()}:: {solusdt[0]} :: mfi:: {mfi_result.value} -- 市场过热，谨慎买入")
      else:  
        pass

    # logger.info(f"{self.candled.position}:: {self.candled.SOLUSDTP[0]} :: mfi:: {mfi_result.value}")

class AlphaHubUnitTest(unittest.TestCase):
  def test_int_time_interval(self):
    self.assertEqual('yes', 'yes')
  
  def test_run(self):
    
    _solusdt_1s, solusdt_1min= get_sol_usdt_1s_and_1min()
    
    sol_candle_feed = PandasCandleFeed(trading_pair=common_trading_pair.SOLUSDT,
                                    timeframe_level=TimeframeType.min1,
                                    dataframe=solusdt_1min)
    
    ontemplationer = AlphaHub(timeframe_level=TimeframeType.min1)
    ontemplationer.add_broker(CommonBroker)
    ontemplationer.add_instrument_amount(amount=1000, instrument=common_product.USDT)
    ontemplationer.add_instrument_amount(amount=1000, instrument=common_product.BTC)
    ontemplationer.add_instrument_amount(amount=1000, instrument=common_product.ETH)
    
    ontemplationer.add_kline(candleFeed=sol_candle_feed)

    ontemplationer.add_strategy(TestStrategy)
    ontemplationer.add_indicator(MoneyFlowIndex)

    ontemplationer.run()
    
    self.assertEqual(True, True)
    
    