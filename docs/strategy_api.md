# TickButcher Strategy API 文档

## 概述

TickButcher的策略系统基于抽象基类`Strategy`和其具体实现`CommonStrategy`。用户需要继承`CommonStrategy`来创建自定义策略。策略的核心逻辑在`next()`方法中实现，通过访问K线数据、持仓信息和下单接口来构建交易逻辑。

策略运行流程：
1. **初始化**：在`init()`方法中设置初始参数、指标等。
2. **数据更新**：AlphaHub引擎按时间推进更新K线数据和指标。
3. **策略执行**：在每个时间点调用`next()`方法执行交易逻辑。
4. **下单**：使用`long_entry()`、`long_close()`等方法提交订单。

## 核心类

### Strategy (抽象基类)

位于[`src/tickbutcher/strategys/__init__.py`](src/tickbutcher/strategys/__init__.py:8)

- **属性**：
  - `alpha_hub: AlphaHub`：策略所属的AlphaHub引擎实例，提供全局访问。

- **方法**：
  - `set_alpha_hub(self, alpha_hub: AlphaHub)`：设置AlphaHub引擎（由框架自动调用）。
  - `init(self)`：抽象方法，策略初始化逻辑（必须实现）。
  - `next(self)`：抽象方法，核心交易逻辑（必须实现）。
  - `long_entry(self, trading_pair: TradingPair, quantity: float, *, order_type: OrderType, price: Optional[float] = None, trading_mode: Optional[TradingMode] = None)`：抽象方法，做多开仓（必须实现）。
  - `long_close(self, trading_pair: TradingPair, *, order_type: OrderType, quantity: Optional[float] = None, price: Optional[float] = None, trading_mode: Optional[TradingMode] = None)`：抽象方法，做多平仓（必须实现）。
  - `short_entry(self, trading_pair: TradingPair, quantity: float, *, order_type: OrderType, price: Optional[float] = None, trading_mode: Optional[TradingMode] = None)`：抽象方法，做空开仓（必须实现）。
  - `short_close(self, trading_pair: TradingPair, quantity: float, *, order_type: OrderType, price: Optional[float] = None, trading_mode: Optional[TradingMode] = None)`：抽象方法，做空平仓（必须实现）。

### CommonStrategy (具体实现)

位于[`src/tickbutcher/strategys/common_strategy.py`](src/tickbutcher/strategys/common_strategy.py:11)

继承自`Strategy`，提供了默认实现和便捷方法。用户应继承此类开发策略。

- **属性**：
  - `broker: Broker`：默认经纪商实例（在`init()`中自动设置）。
  - `account: Account`：默认账户实例（在`init()`中自动设置）。
  - `candled: CandleIndexer`：K线数据索引器，用于访问当前时间点的OHLCV数据。示例：
    ```python
    current_candle = self.candled['BTCUSDT']  # 获取BTCUSDT的当前K线（默认最小时间框架）
    current_candle = self.candled['BTCUSDT_min1'][0]  # 获取当前1分钟K线
    prev_candle = self.candled['BTCUSDT'][-1]  # 获取前一根K线
    ```

- **方法**：
  - `init(self)`：默认初始化，设置`broker`和`account`（可重写扩展）。
  - `next(self)`：默认空实现（必须重写核心逻辑）。
  - `get_open_position(self, trading_pair: TradingPair, pos_side: PosSide, trading_mode: Optional[TradingMode] = None) -> Optional[Position]`：获取指定交易对的开仓位。
    - `pos_side`: PosSide.Long 或 PosSide.Short。
    - `trading_mode`: TradingMode.Isolated（默认永续合约）、Cross 或 Spot。
    - 返回：Position实例或None（无持仓）。
  - `long_entry(self, trading_pair: TradingPair, quantity: float, *, order_type: OrderType, price: Optional[float] = None, trading_mode: Optional[TradingMode] = None)`：做多开仓。
    - `order_type`: OrderType.Market（市价）或 Limit（限价）。
    - `price`: 限价单价格（市价单忽略）。
    - `trading_mode`: 同上，默认根据交易对类型自动设置。
    - 行为：调用broker.submit_order()提交买单（side=OrderSide.Buy, pos_side=PosSide.Long）。
  - `long_close(self, trading_pair: TradingPair, *, order_type: OrderType, quantity: Optional[float] = None, price: Optional[float] = None, trading_mode: Optional[TradingMode] = None)`：做多平仓。
    - `quantity`: 平仓数量（None时平全部仓位）。
    - 其他参数同`long_entry`。
    - 行为：如果quantity=None，自动查询开仓位获取数量；提交卖单（side=OrderSide.Sell, pos_side=PosSide.Long）。
  - `short_entry(self, trading_pair: TradingPair, quantity: float, *, order_type: OrderType, price: Optional[float] = None, trading_mode: Optional[TradingMode] = None)`：做空开仓（默认空实现，需要重写）。
    - 参数同`long_entry`，但提交卖单（side=OrderSide.Sell, pos_side=PosSide.Short）。
  - `short_close(self, trading_pair: TradingPair, quantity: float, *, order_type: OrderType, price: Optional[float] = None, trading_mode: Optional[TradingMode] = None)`：做空平仓（默认空实现，需要重写）。
    - 参数同`long_close`，提交买单（side=OrderSide.Buy, pos_side=PosSide.Short）。

## 使用示例

```python
from tickbutcher.strategys import CommonStrategy
from tickbutcher.brokers.trading_pair import TradingPair
from tickbutcher.order import OrderType, PosSide, TradingMode
from tickbutcher.alphahub import AlphaHub

class MyStrategy(CommonStrategy):
    def init(self):
        super().init()  # 调用父类初始化
        # 初始化指标或其他参数
        pass

    def next(self):
        trading_pair = TradingPair.get_trading_pair('BTCUSDT')
        
        # 获取当前K线
        current = self.candled[trading_pair][0]  # 当前K线OHLCV
        
        # 简单策略：如果收盘价 > 开盘价，做多
        if current['close'] > current['open']:
            self.long_entry(
                trading_pair=trading_pair,
                quantity=0.01,
                order_type=OrderType.Market,
                trading_mode=TradingMode.Isolated
            )
        
        # 检查持仓并平仓
        position = self.get_open_position(trading_pair, PosSide.Long)
        if position and current['close'] < current['open']:
            self.long_close(
                trading_pair=trading_pair,
                order_type=OrderType.Market
            )

# 在AlphaHub中使用
hub = AlphaHub(timeframe_level=TimeframeType.sec1)  # 支持秒级
hub.add_strategy(MyStrategy)
hub.run()  # 开始回测/实盘
```

## 注意事项

- **时间框架**：策略运行在AlphaHub指定的最小时间框架（如sec1支持秒级回测）。
- **数据访问**：使用`candled`属性访问K线，支持多时间框架（如`self.candled['BTCUSDT_min5']`）。
- **下单参数**：
  - `TradingPair`：通过`TradingPair.get_trading_pair('ID')`获取。
  - `OrderType`：Market（市价，无需price）、Limit（限价，必须提供price）。
  - `TradingMode`：Isolated（逐仓，默认永续）、Cross（全仓）、Spot（现货）。
- **事件处理**：订单和持仓变化通过Broker的事件监听器处理（可自定义监听）。
- **回测支持**：AlphaHub的`run()`方法支持历史数据回测，按时间推进执行`next()`。

更多细节请参考源代码：
- [`Strategy`](src/tickbutcher/strategys/__init__.py:8)
- [`CommonStrategy`](src/tickbutcher/strategys/common_strategy.py:11)
- [`CandleIndexer`](src/tickbutcher/candlefeed/__init__.py:24)