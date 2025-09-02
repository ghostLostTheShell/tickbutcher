
import unittest
from unittest.mock import Mock

from tests.dataset import get_sol_usdt_1s_and_1min
from tickbutcher.brokers.account import Account
from tickbutcher.brokers.position import Position, PositionStatus
from tickbutcher.order import Order, OrderSide, OrderStatus, OrderType, PosSide, TradingMode
from tickbutcher.products import common as comm_fi
from tickbutcher.brokers.trading_pair import common as common_tp



class PositionTest(unittest.TestCase):
  def test_ps_isolated_position(self):
    """测试永续合约的逐仓仓位"""
    _sol_usdt_1s_dataframe, _ = get_sol_usdt_1s_and_1min()  # 预加载数据集
    
    pos = Position(1, base=comm_fi.SOL, pos_side=PosSide.Long, trading_mode=TradingMode.Isolated)

    mock_account = Mock(spec=Account)
    mock_account.id = 4

    order = Order(trading_mode=TradingMode.Isolated,
                  trading_pair=common_tp.SOLUSDTP,
                  order_type=OrderType.Market,
                  quantity=100,
                  side=OrderSide.Buy,
                  account=mock_account)
    
    order.execution_price = 23.5
    order.execution_quantity = 100
    order.commission = 0.1
    order.comm_settle_asset = comm_fi.USDT
    order.status = OrderStatus.Completed
    order.set_id(1)
    pos.add_order(order)
    self.assertEqual(pos.entry_price, 23.5)
    self.assertEqual(pos.amount, 100)
    self.assertEqual(pos.status, PositionStatus.Active)
    self.assertEqual(pos.pos_side, PosSide.Long)
    self.assertEqual(pos.trading_mode, TradingMode.Isolated)
    
    
    order = Order(trading_mode=TradingMode.Isolated,
                  trading_pair=common_tp.SOLUSDTP,
                  order_type=OrderType.Market,
                  quantity=100,
                  side=OrderSide.Buy,
                  account=mock_account)
    
    order.execution_price = 20.5
    order.execution_quantity = 100
    order.commission = 0.1
    order.comm_settle_asset = comm_fi.USDT
    order.status = OrderStatus.Completed
    order.set_id(1)
    pos.add_order(order)

    self.assertEqual(pos.entry_price, (23.5 * 100 + 20.5 * 100) / 200)
    self.assertEqual(pos.amount, 200)
    self.assertEqual(pos.status, PositionStatus.Active)
    self.assertEqual(pos.pos_side, PosSide.Long)
    self.assertEqual(pos.trading_mode, TradingMode.Isolated)
    
    