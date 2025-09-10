"""测试指标运行"""

from tests.dataset import get_sol_usdt_1s_and_1min
from tickbutcher import Contemplationer
from tickbutcher.Indicators.mfi import MoneyFlowIndex
from tickbutcher.brokers.common_broker import CommonBroker
from tickbutcher.brokers.trading_pair.common import SOLUSDTP
from tickbutcher.candlefeed import TimeframeType
from tickbutcher.candlefeed.pandascandlefeed import PandasCandleFeed
from tickbutcher.strategys import CommonStrategy



class TestStrategy(CommonStrategy):
  
  def next(self):
    mfi = self.contemplationer.get_indicator('mfi', MoneyFlowIndex) 
    
    # _mfi.get_result()
    print(f"{self.candled.position}:: {self.candled.SOLUSDTP[0]} :: mfi:: {mfi.get_curret_result(SOLUSDTP)}")

solusdt_1s, solusdt_1min= get_sol_usdt_1s_and_1min()

sol_candle_feed = PandasCandleFeed(trading_pair=SOLUSDTP,
                                    timeframe_level=TimeframeType.min1,
                                    dataframe=solusdt_1min)
# sol_candle_feed.load_data(solusdt_1min, TimeframeType.min1)

broker = CommonBroker()
ontemplationer = Contemplationer(timeframe_level=TimeframeType.min1, 
                                 brokers=[broker])

ontemplationer.add_kline(candleFeed=sol_candle_feed)

ontemplationer.add_strategy(TestStrategy)
ontemplationer.add_indicator(MoneyFlowIndex)

ontemplationer.run()

