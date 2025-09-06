
from typing import Dict, List, TYPE_CHECKING, Optional, Set

from tickbutcher.brokers import OrderStatusEvent, PositionStatusEvent
from tickbutcher.brokers import OrderStatusEvent
from tickbutcher.commission import CommissionType
from tickbutcher.log import logger
from tickbutcher.order import OrderSide, OrderStatus, OrderType



# 在运行时这个导入不会被执行，从而避免循环导入
if TYPE_CHECKING:
  from tickbutcher.brokers import Broker
  from tickbutcher.brokers.position import Position
  from tickbutcher.brokers.trading_pair import TradingPair
  from tickbutcher.order import Order
  from tickbutcher.order import PosSide, TradingMode
  from tickbutcher.brokers.margin import MarginType
  from tickbutcher.products import AssetType

class CollateralMargin:
  """账户下某个仓位的保证金信息"""
  position: 'Position'
  amount: float
  asset_type: 'AssetType'

  def __init__(self, position: 'Position', amount: float, asset_type: 'AssetType'):
    self.position = position
    self.amount = amount
    self.asset_type = asset_type
    
class Account(object):
  id: int
  default_leverage:int
  asset_value_map: Dict['AssetType', float]
  trading_pair_leverage:Dict['TradingPair', int]
  trading_pair_margin_type: Dict['TradingPair', 'MarginType'] # TODO 修改为仓位模式
  #保证金相关的属性
  collateral_margin_list: List['CollateralMargin'] # 该账户下所有仓位的保证金
  _collateral_margin_map: Dict['Position', 'CollateralMargin']
  
  order_list: Set['Order']
  position_list: List['Position']
  active_position_list: List['Position']
  broker: 'Broker' # 所属的经纪商

  def __init__(self, *, id: int, broker:'Broker'):
    self.id = id
    self.asset_value_map = {}
    self.trading_pair_leverage = {}
    self.default_leverage = 1
    self.order_list = set()
    self.position_list = []
    self.broker = broker
    self.collateral_margin_list = []
    self._collateral_margin_map = {}

  def get_collateral_margin(self, position: 'Position') -> float:
    """获取指定仓位的保证金"""
    collateral_margin = self._collateral_margin_map.get(position)
    return collateral_margin.amount if collateral_margin else 0.0

  def add_margin(self, amount: float, position: 'Position'):
    """增加保证金"""
    collateral_margin = self._collateral_margin_map.get(position)
    if collateral_margin:
      collateral_margin.amount += amount
    else:
      collateral_margin = CollateralMargin(
          position=position,
          amount=amount,
          asset_type=position.trading_pair.quote.type
      )
      self.collateral_margin_list.append(collateral_margin)
      self._collateral_margin_map[position] = collateral_margin


  def reduce_margin(self, amount: float, position: 'Position'):
    """减少保证金"""
    collateral_margin = self._collateral_margin_map.get(position)
    if collateral_margin:
      collateral_margin.amount -= amount
      if collateral_margin.amount <= 0:
        self.collateral_margin_list.remove(collateral_margin)
      return
  
    raise ValueError(f"没有找到对应的保证金信息: {position}")
  
  def handle_ps_market_order(self, order: 'Order'):
    """处理永续合约市价单"""
    
    trading_pair = order.trading_pair
    current = self.broker.get_contemplationer().candle[0, order.trading_pair.id]
    order.execution_price = current.close
    order.execution_quantity = order.quantity
    #计算本次交易的手续费
    commission = self.broker.get_commission(trading_pair)
    match (commission.commission_type, order.side):
      case (CommissionType.MakerTaker, OrderSide.Buy) :
        
        commission_value = commission.calculate(order.execution_quantity)
        order.set_commission(commission_value, trading_pair.base)
        
      case _:
        commission_value = commission.calculate(order.execution_price * order.execution_quantity)
        order.set_commission(commission_value, trading_pair.quote)
    
    
    match (order.trading_mode, order.pos_side, order.side):
      #逐仓模式
      case (TradingMode.Isolated, PosSide.Long, OrderSide.Buy):
        # 逐仓开多仓或追加多仓()
        # 检查仓位是否存在
        position = self.get_open_position(trading_pair, trading_mode=TradingMode.Isolated, pos_side=PosSide.Long)
        if not position:
          # 创建新仓位
          position = Position(id=self.broker.generate_position_id(),
                              account=self,
                              trading_pair=trading_pair,
                              pos_side=PosSide.Long,
                              trading_mode=TradingMode.Isolated)
          # 增加仓位到经纪商和账户
          self.add_position(position)

        # 增加仓位保证金
        position_leverage = self.get_leverage(trading_pair)
        margin = order.execution_quantity * order.execution_price / position_leverage
        self.add_margin(margin, position)

        # 进行交易
        if order.comm_settle_asset is order.trading_pair.base:
          self.deposit(order.execution_quantity - order.commission, trading_pair.base.type)  
        else: 
          self.deposit(order.execution_quantity, trading_pair.base.type)
        
        
        order.status = OrderStatus.Completed
        self.broker.trigger_order_changed_event(OrderStatusEvent(order=order, event_type=order.status))
        position.add_order(order)
        self.broker.trigger_position_changed_event(PositionStatusEvent(position=position, event_type='Active'))
        
      case (TradingMode.Isolated, PosSide.Long, OrderSide.Sell):
        # 逐仓多仓平仓
        position = self.get_open_position(trading_pair, trading_mode=TradingMode.Isolated, pos_side=PosSide.Long)
        if position is None:
          logger.warning(f"没有找到对应的仓位: {trading_pair} {order.trading_mode} {order.pos_side}")
          order.status = OrderStatus.Rejected
        else:
          position_leverage = self.get_leverage(trading_pair)
          margin = order.execution_quantity * order.execution_price / position_leverage
          #计算盈利
          position.add_order(order)

      case (TradingMode.Isolated, PosSide.Short, OrderSide.Buy):
        # 逐仓空仓平仓
        pass
      case (TradingMode.Isolated, PosSide.Short, OrderSide.Sell):
        # 逐仓空仓或追加空仓()
        pass
      
      # 全仓模式
      case (TradingMode.Cross, PosSide.Long, OrderSide.Buy):
        # 全仓模式下，开多仓
        self.deposit(order.execution_quantity * order.execution_price, trading_pair.quote.type)
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
        order.status = OrderStatus.Rejected
        self.broker.trigger_order_changed_event(OrderStatusEvent(order=order, event_type=order.status))
      

  def handle_spot_market_order(self, order: 'Order'):
    """处理现货市价单"""
    trading_pair = order.trading_pair
    current = self.broker.get_contemplationer().candle[0, order.trading_pair.id]
    order.execution_price = current.close
    order.execution_quantity = order.quantity
    #计算本次交易的手续费
    commission = self.broker.get_commission(trading_pair)
    match (commission.commission_type, order.side):
      case (CommissionType.MakerTaker, OrderSide.Buy) :          
        commission_value = commission.calculate(order.execution_quantity)
        order.set_commission(commission_value, trading_pair.base)
        
      case _:
        commission_value = commission.calculate(order.execution_price * order.execution_quantity)
        order.set_commission(commission_value, trading_pair.quote)
    
    match order.side:
      case OrderSide.Buy:
        if order.comm_settle_asset is order.trading_pair.base:
          self.deposit(order.execution_quantity - order.commission, trading_pair.base.type)  
        else: 
          self.deposit(order.execution_quantity, trading_pair.base.type)
          
        position = self.get_open_position(trading_pair, trading_mode=TradingMode.Spot)
        
        if not position:
          # 创建新仓位
          position = Position(id=self.broker.generate_position_id(),
                              account=self,
                              trading_pair=trading_pair,
                              pos_side=PosSide.Long,
                              trading_mode=TradingMode.Spot)
          # 增加仓位到经纪商和账户
          self.add_position(position)
          self.broker.trigger_position_changed_event(PositionStatusEvent(position=position, event_type='Active'))
        
        position.add_order(order)
        
      case OrderSide.Sell:
        
        position = self.get_open_position(trading_pair, trading_mode=TradingMode.Spot)
        if position is None:
          logger.error(f"没有找到对应的仓位: {trading_pair} {order.trading_mode} {order.pos_side}")
          raise SystemError(f"没有找到对应的仓位: {trading_pair} {order.trading_mode} {order.pos_side}")
        
        if order.comm_settle_asset is order.trading_pair.quote:
          self.deposit(order.execution_price * order.execution_quantity - order.commission, trading_pair.quote.type)  
        else: 
          self.deposit(order.execution_price * order.execution_quantity, trading_pair.quote.type)

        position.add_order(order)
        if not position.is_closed():
          self.broker.trigger_position_changed_event(PositionStatusEvent(position=position, event_type=position.status.name))
        
      case _:
        raise SystemError(f"不支持的订单方向: {order.side}")
    
    order.status = OrderStatus.Completed
    self.broker.trigger_order_changed_event(OrderStatusEvent(order=order, event_type=order.status))

  def handle_spot_limit_order(self, order: 'Order'):
    """处理现货限价单"""
    trading_pair = order.trading_pair
    current = self.broker.get_contemplationer().candle[0, order.trading_pair.id]
    order.execution_price = current.close
    order.execution_quantity = order.quantity
    #计算本次交易的手续费
    commission = self.broker.get_commission(trading_pair)
    match (commission.commission_type, order.side):
      case (CommissionType.MakerTaker, OrderSide.Buy) :
        
        commission_value = commission.calculate(order.execution_quantity)
        order.set_commission(commission_value, trading_pair.base)
        
      case _:
        commission_value = commission.calculate(order.execution_price * order.execution_quantity)
        order.set_commission(commission_value, trading_pair.quote)
    
    match order.side:
      case OrderSide.Buy:
        if order.price >= current.close:
          if order.comm_settle_asset is order.trading_pair.base:
            self.deposit(order.execution_quantity - order.commission, trading_pair.base.type)  
          else: 
            self.deposit(order.execution_quantity, trading_pair.base.type)
            
          position = self.get_open_position(trading_pair, trading_mode=TradingMode.Spot)
          
          if not position:
            # 创建新仓位
            position = Position(id=self.broker.generate_position_id(),
                                account=self,
                                trading_pair=trading_pair,
                                pos_side=PosSide.Long,
                                trading_mode=TradingMode.Spot)
            # 增加仓位到经纪商和账户
            self.add_position(position)
            self.broker.trigger_position_changed_event(PositionStatusEvent(position=position, event_type='Active'))
          
          position.add_order(order)
          order.status = OrderStatus.Completed
          self.broker.trigger_order_changed_event(OrderStatusEvent(order=order, event_type=order.status))
          
        else:
          pass
      case OrderSide.Sell:
        if order.price <= current.close:
          position = self.get_open_position(trading_pair, trading_mode=TradingMode.Spot)
          if position is None:
            logger.error(f"没有找到对应的仓位: {trading_pair} {order.trading_mode} {order.pos_side}")
            raise SystemError(f"没有找到对应的仓位: {trading_pair} {order.trading_mode} {order.pos_side}")
          
          if order.comm_settle_asset is order.trading_pair.quote:
            self.deposit(order.execution_price * order.execution_quantity - order.commission, trading_pair.quote.type)  
          else: 
            self.deposit(order.execution_price * order.execution_quantity, trading_pair.quote.type)

          position.add_order(order)
          if not position.is_closed():
            self.broker.trigger_position_changed_event(PositionStatusEvent(position=position, event_type=position.status.name))
          
          order.status = OrderStatus.Completed
          self.broker.trigger_order_changed_event(OrderStatusEvent(order=order, event_type=order.status))
        else:
          pass
        
      case _:
        raise SystemError(f"不支持的订单方向: {order.side}")
      
    if order.status is OrderStatus.Pending or order.status is OrderStatus.PartiallyFilled:
      #计算本次交易的手续费
      self.broker.add_pending_order(order)
      # commission = self.broker.get_commission(trading_pair)
    else:
      self.broker.remove_pending_order(order)

  def process_order(self, order: 'Order'):
    self.order_list.add(order)
    
    # 处理交易
    match (order.trading_pair.base.type, order.order_type):
      case (AssetType.PerpetualSwap, OrderType.Market):
        self.handle_ps_market_order(order)
      case (AssetType.PerpetualSwap, OrderType.Limit):
        pass
      case (AssetType.STOCK, OrderType.Market) | (AssetType.CRYPTO, OrderType.Market):
        self.handle_spot_market_order(order)
      case (AssetType.STOCK, OrderType.Limit) | (AssetType.CRYPTO, OrderType.Limit):
        self.handle_spot_limit_order(order)
      case _:
        raise ValueError(f"不支持的订单类型: {order.order_type} for {order.trading_pair.base.type}")

  # 查询可用资产
  def get_available_asset(self, asset_type: 'AssetType') -> float:
    for collateral_margin in self.collateral_margin_list:
      if collateral_margin.asset_type == asset_type:
        margin = collateral_margin.amount
        break
    else:
      margin = 0.0

    return self.asset_value_map.get(asset_type, 0.0) - margin

  def set_margin_type(self, margin_type: 'MarginType', trading_pair: 'TradingPair'):
    self.trading_pair_margin_type[trading_pair] = margin_type

  def get_margin_type(self, trading_pair: 'TradingPair') -> 'MarginType':
    if trading_pair not in self.trading_pair_margin_type:
      self.trading_pair_margin_type[trading_pair] = MarginType.Isolated

    return self.trading_pair_margin_type.get(trading_pair, MarginType.Isolated)
  

  def set_leverage(self, leverage: int, trading_pair: 'TradingPair'):
    self.trading_pair_leverage[trading_pair] = leverage

  def get_leverage(self, trading_pair: 'TradingPair') -> int:
    if trading_pair not in self.trading_pair_leverage.keys():
      self.trading_pair_leverage[trading_pair] = self.default_leverage
      
    return self.trading_pair_leverage.get(trading_pair, self.default_leverage)  

  def deposit(self, amount: float, asset_type: 'AssetType', ):
    """
    存入
    """
    self.asset_value_map[asset_type] = self.asset_value_map.get(asset_type, 0) + amount

  def withdraw(self, amount: float, asset_type: 'AssetType', ):
    """
    取出
    """
    self.asset_value_map[asset_type] = self.asset_value_map.get(asset_type, 0) - amount

  def get_open_position(self, 
                   trading_pair: 'TradingPair', 
                   *, 
                   trading_mode: 'TradingMode', 
                   pos_side: Optional['PosSide']=None):
    if trading_mode is TradingMode.Spot:
      pos_side = PosSide.Long
    
    for position in self.position_list:
      
      if position.is_active() and position.trading_pair == trading_pair and position.trading_mode is trading_mode and position.pos_side is pos_side:
        return position
    return None

  def add_position(self, position: 'Position'):
    self.position_list.append(position)