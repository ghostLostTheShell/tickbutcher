
from typing import TYPE_CHECKING, Dict, List, Optional
from tickbutcher.brokers.account import Account
from tickbutcher.brokers.position import Position
from tickbutcher.brokers.trading_pair import TradingPair
from tickbutcher.commission import Commission, CommissionType, MakerTakerCommission
from tickbutcher.order import Order, OrderStatus, OrderType, OrderSide
from tickbutcher.brokers import Broker, OrderStatusEventCallback, PositionStatusEvent, OrderStatusEvent, PositionStatusEventCallback
from tickbutcher.products import AssetType

if TYPE_CHECKING:
  from tickbutcher.contemplationer import Contemplationer
  from tickbutcher.order import PosSide,TradingMode
class CommonBroker(Broker):
  contemplationer:'Contemplationer'
  order_changed_event_listener: List[OrderStatusEventCallback]
  position_changed_event_listener: List[PositionStatusEventCallback]
  order_list: List[Order]
  order_completed_list: List[Order]
  position_list: List[Position]
  _accounts:List[Account]
  tradingPair_commission_map: Dict[TradingPair, Commission]

  def __init__(self):
    self.order_list = []
    self.order_completed_list = []
    self.position_list = []
    self._accounts = []
    self.default_commission = MakerTakerCommission(0.02, 0.05)
    self.default_ps_commission = MakerTakerCommission(0.02, 0.05, c_type=CommissionType.MakerTakerOnQuote)
    self.order_changed_event_listener = []
    self.position_changed_event_listener = [] 

  def set_commission(self, trading_pair: TradingPair, commission:Commission):
    self.tradingPair_commission_map[trading_pair] = commission
  
  def get_commission(self, trading_pair: TradingPair)->Commission:
    result = self.tradingPair_commission_map.get(trading_pair)
    if result is None:
      match trading_pair.base.type:
        case AssetType.PerpetualSwap:
          self.tradingPair_commission_map.setdefault(trading_pair, self.default_ps_commission)
          result = self.default_ps_commission
        case _:
          self.tradingPair_commission_map.setdefault(trading_pair, self.default_commission)
          result = self.default_commission
        
    return result

  @property
  def accounts(self):
    return self._accounts
  
  def register_account(self):
    account_id = self.generate_account_id()
    account = Account(id=account_id, broker=self)
    self._accounts.append(account)
    return account
    
  def set_contemplationer(self, contemplationer: 'Contemplationer'):
    self.contemplationer = contemplationer


  def trigger_order_changed_event(self, event: OrderStatusEvent):
    """
    触发事件
    """
    for listener in self.order_changed_event_listener:
      listener(event) 

  def add_order_changed_event_listener(self, listener: OrderStatusEventCallback):
    """
    添加事件监听器
    """
    self.order_changed_event_listener.append(listener)


  def remove_order_changed_event_listener(self, listener: OrderStatusEventCallback):
    """
    移除事件监听器
    """
    self.order_changed_event_listener.remove(listener)


  def trigger_position_changed_event(self, event: PositionStatusEvent):
    """
    触发事件
    """
    for listener in self.position_changed_event_listener:
      listener(event)

  def add_position_changed_event_listener(self, listener: PositionStatusEventCallback):
    """
    添加事件监听器
    """
    self.position_changed_event_listener.append(listener)

  def remove_position_changed_event_listener(self, listener: PositionStatusEventCallback):
    """
    移除事件监听器
    """
    self.position_changed_event_listener.remove(listener)
    
    

  def get_order_list(self, account: Account, 
                     *, 
                     trading_pairs: Optional[List[TradingPair]]=None,
                     ) -> List[Order]:
    
    
    return []

  def get_position_list(self, 
                        account: Account, 
                        *, 
                        trading_pairs: Optional[List[TradingPair]]=None, # 过滤交易对
                        ) -> List[Position]:
    return []
  
  def next(self):
    pass
  
  

  
  def handle_ps_market_order(self, order: Order):
    """处理永续合约市价单"""
    
    trading_pair = order.trading_pair
    account =order.account
    current = self.contemplationer.candle[0, order.trading_pair.id]
    order.execution_price = current.close
    order.execution_quantity = order.quantity
    #计算本次交易的手续费
    commission = self.get_commission(trading_pair)
    match (commission.commission_type, order.side):
      case (CommissionType.MakerTaker, OrderSide.Buy) :
        commission_value = commission.calculate(order.execution_quantity)
        order.set_commission(commission_value, trading_pair.base)
      case _:
        commission_value = commission.calculate(order.execution_price * order.execution_quantity)
        order.set_commission(commission_value, trading_pair.quote)
    
    #计算保证金
    
    #执行交易
    
    match (order.trading_mode, order.pos_side, order.side, ):
      #逐仓模式
      case (TradingMode.Isolated, PosSide.Long, OrderSide.Buy):
        # 逐仓开多仓或追加多仓()
        # 检查仓位是否存在
        account.deposit(order.execution_quantity * order.execution_price, trading_pair.quote.type)
        pass
      case (TradingMode.Isolated, PosSide.Long, OrderSide.Sell):
        # 逐仓多仓平仓
        pass
      case (TradingMode.Isolated, PosSide.Short, OrderSide.Buy):
        # 逐仓空仓平仓
        pass
      case (TradingMode.Isolated, PosSide.Short, OrderSide.Sell):
        # 逐仓空仓或追加空仓()
        pass
      
      # 全仓模式
      case (TradingMode.Cross, PosSide.Long, OrderSide.Buy):
        # 全仓模式下，开多仓
        account.deposit(order.execution_quantity * order.execution_price, trading_pair.quote.type)
        pass
      case (TradingMode.Cross, PosSide.Long, OrderSide.Sell):
        # 全仓模式下，平多仓
        pass
      case (TradingMode.Cross, PosSide.Short, OrderSide.Buy):
        # 全仓模式下，平空仓
        pass
      case (TradingMode.Cross, PosSide.Short, OrderSide.Sell):
        # 全仓模式下，开空仓
        pass
      case _:
        raise ValueError(f"不支持的交易模式: {order.trading_mode} for {order.pos_side} and {order.side}")
      
      
    #扣除手续费
    account.withdraw(order.commission, order.comm_settle_asset.type)
    
    
    
    # 创建仓位
    position = Position(id=self.generate_position_id(),
                        tradingPair=trading_pair)
    self.position_list.append(position)

    # 设置asset_value_list
    match trading_pair.base.type:
      case AssetType.PerpetualSwap:
        pass
      case _:
        pass


  def submit_order(self, *,
                  account: 'Account',
                  trading_pair: TradingPair,
                  order_type: OrderType,
                  side: OrderSide,
                  trading_mode:'TradingMode',
                  quantity: float,
                  pos_side: Optional[PosSide]=None,
                  price: Optional[int] = None,
                  reduce_only:Optional[bool]=None
                   ) -> None:
    # 创建订单

    order = Order(
      trading_mode=trading_mode,
      trading_pair=trading_pair,
      quantity=quantity,
      side=side,
      order_type=order_type,
      price=price,
      account=account,
      pos_side=pos_side,
      reduce_only=reduce_only,
    )
    
    order.status = OrderStatus.Created
    order.created_at = self.contemplationer.current_time
    order.set_id(self.generate_order_id())
    self.trigger_order_changed_event(OrderStatusEvent(order=order, event_type=OrderStatus.Created))
    self.order_list.append(order)
    
    
    # 检查订单信息是否有错误
    pass
    # 
    # 处理交易
    match (order.trading_pair.base.type, order.order_type):
      case (AssetType.PerpetualSwap, OrderType.MarketOrder):
        self.handle_ps_market_order(order)
      case (AssetType.PerpetualSwap, OrderType.LimitOrder):
        pass
      
      case _:
        raise ValueError(f"不支持的订单类型: {order.order_type} for {order.trading_pair.base.type}")




  
  def generate_order_id(self) -> int:
    """生成订单id"""
    if len(self.order_list) == 0:
      return 0
    else:
      return self.order_list[-1].id + 1

  def generate_position_id(self) -> int:
    """生成交易id"""
    if len(self.position_list) == 0:
      return 0
    else:
      return self.position_list[-1].id + 1
    
    
  def generate_account_id(self) -> int:
    """生成账户id"""
    if len(self._accounts) == 0:
      return 0
    else:
      return self._accounts[-1].id + 1