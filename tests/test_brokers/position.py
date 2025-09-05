
import unittest
from unittest.mock import Mock

from tests.dataset import get_sol_usdt_1s_and_1min
from tickbutcher.brokers.account import Account
from tickbutcher.brokers.common_broker import CommonBroker
from tickbutcher.brokers.position import Position, PositionStatus
from tickbutcher.candlefeed import TimeframeType
from tickbutcher.candlefeed.pandascandlefeed import PandasCandleFeed
from tickbutcher.contemplationer import Contemplationer
from tickbutcher.order import Order, OrderSide, OrderStatus, OrderType, PosSide, TradingMode
from tickbutcher.products import FinancialInstrument, common as comm_fi
from tickbutcher.brokers.trading_pair import TradingPair, common as common_tp

def make_market_isolated_order(*,
                        account:'Account',
                        id:int,
                        quantity:int,
                        side: 'OrderSide',
                        execution_price: float,
                        execution_quantity:float,
                        commission: float=0.003,
                        comm_settle_asset: 'FinancialInstrument'=comm_fi.USDT,
                        trading_pair: 'TradingPair'=common_tp.SOLUSDTP,
                        ):

    order = Order(trading_mode=TradingMode.Isolated,
                  trading_pair=trading_pair,
                  order_type=OrderType.Market,
                  quantity=quantity,
                  side=side,
                  account=account)

    order.execution_price = execution_price
    order.execution_quantity = execution_quantity
    order.commission = commission
    order.comm_settle_asset = comm_settle_asset
    order.status = OrderStatus.Completed
    order.set_id(id)
    return order


class PositionTest(unittest.TestCase):
  def test_ps_isolated_position(self):
    """测试永续合约的逐仓仓位"""
    _sol_usdt_1s_dataframe, solusdt_1min = get_sol_usdt_1s_and_1min()  # 预加载数据集
    sol_candle_feed = PandasCandleFeed(trading_pair=common_tp.SOLUSDTP,
                                       timeframe_level=TimeframeType.sec1,
                                       dataframe=_sol_usdt_1s_dataframe)
    sol_candle_feed.load_data(solusdt_1min, TimeframeType.min1)

    broker = CommonBroker()
    ontemplationer = Contemplationer(timeframe_level=TimeframeType.sec1, brokers=[broker])
    ontemplationer.add_kline(candleFeed=sol_candle_feed)
    _mock_ontemplationer = Mock(wraps=ontemplationer)

    account = broker.register_account()
    mock_account = Mock(wraps=account)
    
    pos = Position(1, 
                   account=mock_account, # type: ignore
                   pos_side=PosSide.Long, 
                   trading_mode=TradingMode.Isolated)

    mock_account = Mock(spec=Account)
    mock_account.id = 4

    order = make_market_isolated_order(account=mock_account,
                                        id=1,
                                        quantity=100,
                                        side=OrderSide.Buy,
                                        execution_price=23.5,
                                        execution_quantity=100)
    order.status = OrderStatus.Completed
    pos.add_order(order)
    # print(pos)
    self.assertEqual(pos.entry_price, 23.5)
    self.assertEqual(pos.amount, 100)
    self.assertEqual(pos.status, PositionStatus.Active)
    self.assertEqual(pos.pos_side, PosSide.Long)
    self.assertEqual(pos.trading_mode, TradingMode.Isolated)
    
    
    order = make_market_isolated_order(account=mock_account,
                                        id=2,
                                        quantity=100,
                                        side=OrderSide.Buy,
                                        execution_price=10.5,
                                        execution_quantity=100)
    pos.add_order(order)
    # print(pos)
    self.assertEqual(pos.entry_price, (23.5 * 100 + 10.5 * 100) / 200)
    self.assertEqual(pos.amount, 200)
    self.assertEqual(pos.status, PositionStatus.Active)
    self.assertEqual(pos.pos_side, PosSide.Long)
    self.assertEqual(pos.trading_mode, TradingMode.Isolated)
    
    order = make_market_isolated_order(account=mock_account,
                                        id=3,
                                        quantity=50,
                                        side=OrderSide.Sell,
                                        execution_price=10.5,
                                        execution_quantity=100)
    pos.add_order(order)
    self.assertEqual(pos.entry_price, (23.5 * 100 + 10.5 * 100) / 200)
    self.assertEqual(pos.amount, 100)
    self.assertEqual(pos.status, PositionStatus.Active)
    self.assertEqual(pos.pos_side, PosSide.Long)
    self.assertEqual(pos.trading_mode, TradingMode.Isolated)