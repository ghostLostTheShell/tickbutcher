
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
    mfi_result = mfi.get_current_result(common_trading_pair.SOLUSDT, TimeframeType.min1)
    solusdt = self.candled.SOLUSDT
    if mfi_result is None:
      return
    else:
      if mfi_result.signal_strength > 0.4 and mfi_result.signal_strength < 0.8:
        # logger.info(f"{solusdt.get_iso_datetime()}:: {solusdt[0]} :: mfi:: {mfi_result.value} -- 买入信号")
        self.long_entry(common_trading_pair.SOLUSDT,
          quantity=0.05 * mfi_result.signal_strength,
          order_type=OrderType.Market)
        
      elif mfi_result.signal_strength <= -0.6 and mfi_result.signal_strength > -0.7:
        # logger.info(f"{solusdt.get_iso_datetime()}:: {solusdt[0]} :: mfi:: {mfi_result.value} -- 卖出信号")
         self.long_close(common_trading_pair.SOLUSDT, order_type=OrderType.Market)
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

    alpha_hub = AlphaHub(timeframe_level=TimeframeType.min1)
    alpha_hub.add_broker(CommonBroker)
    alpha_hub.add_instrument_amount(amount=1000, instrument=common_product.USDT)
    alpha_hub.add_instrument_amount(amount=1000, instrument=common_product.BTC)
    alpha_hub.add_instrument_amount(amount=1000, instrument=common_product.ETH)

    alpha_hub.add_kline(candleFeed=sol_candle_feed)
    alpha_hub.add_strategy(TestStrategy)
    alpha_hub.add_indicator('mfi', MoneyFlowIndex, exclude_timeframes={TimeframeType.sec1})

    alpha_hub.run()
    
    broker = alpha_hub.get_broker(CommonBroker)
    
    
    
    for account in broker.accounts:
      
      # for order in account.order_list:
      #   print(order)
       
      print("------------------------")

      for position in account.position_list:
        print(position)

      print("========================")
      for instrument, value in account.instrument_value_map.items():
        alpha_hub.candle_list
        usdt_value = 0.0
        if instrument.symbol == 'USDT':
          usdt_value = value
        if instrument.symbol == 'BTC':
          usdt_value = 0.0
        if instrument.symbol == 'ETH':
          usdt_value = 0.0
        elif instrument.symbol == 'SOL':
          usdt_value = value * alpha_hub.candle[0, 'SOLUSDT'].close
        
        logger.info(f"账户资产: {instrument.symbol} :: {value} udst价值: {usdt_value} ")
    
    self.assertEqual(True, True)
    
    