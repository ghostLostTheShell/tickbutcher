import unittest
from unittest.mock import Mock
from tests.dataset import get_sol_usdt_1s_and_1min
from tickbutcher.brokers.common_broker import CommonBroker
from tickbutcher.candlefeed import TimeframeType
from tickbutcher.candlefeed.pandascandlefeed import PandasCandleFeed
from tickbutcher.brokers.trading_pair import common as common_trading_pair
from tickbutcher.contemplationer import Contemplationer


class CommonBrokerTest(unittest.TestCase):

  def get_ontemplationer_on_candle_feed(self, candle_feed:PandasCandleFeed) -> Contemplationer:
    """获取一个 mock 的 Contemplationer 对象
    """

    current_time = candle_feed.get_position_index_list()[0]

    ontemplationer = Mock()
    # brokers: List['Broker']
    # strategys: List['Strategy']
    ontemplationer.candle_list = [candle_feed]
    ontemplationer.trading_pair_candle_table =  {candle_feed.trading_pair: candle_feed}
    ontemplationer.current_time = current_time
    ontemplationer.timeframe_level = TimeframeType.sec1

    return ontemplationer

  # 订单提交测试
  def test_market_order_submission(self):
    """市价单提交测试
    """
    solusdt_1s, solusdt_1min= get_sol_usdt_1s_and_1min()
    sol_candle_feed = PandasCandleFeed(trading_pair=common_trading_pair.SOLUSDTP,
                                       timeframe_level=TimeframeType.sec1,
                                       dataframe=solusdt_1s)
    sol_candle_feed.load_data(solusdt_1min, TimeframeType.min1)
  
    broker = CommonBroker()
    ontemplationer = Contemplationer(timeframe_level=TimeframeType.sec1, brokers=[broker])
    ontemplationer.add_kline(candleFeed=sol_candle_feed)
    _mock_ontemplationer = Mock(wraps=ontemplationer)

    _account = broker.register_account()
    
    ontemplationer.current_time = solusdt_1s.index[0]
    
    # broker.submit_order(
    #     trading_pair=common_trading_pair.SOLUSDTP,
    #     order_type=OrderType.MarketOrder,
    #     side=OrderSide.Buy,
    #     quantity=100,
    #     account=account
    # )
    
    

    # # 断言订单是否成功提交
    # self.assertTrue(broker.order_manager.has_pending_order())
    # self.assertEqual(broker.order_manager.get_pending_order().trading_pair, common_trading_pair.SOLUSDTP)
    # self.assertEqual(broker.order_manager.get_pending_order().order_option_type, OrderType.MarketOrder)
    # self.assertEqual(broker.order_manager.get_pending_order().side, OrderSide.Buy)
    # self.assertEqual(broker.order_manager.get_pending_order().quantity, 100)
    # self.assertEqual(broker.order_manager.get_pending_order().status, OrderStatus.Filled)
    
    