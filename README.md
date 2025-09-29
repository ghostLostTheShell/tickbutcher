# TickButcher

一个轻量级、高性能的量化交易框架，专注于简洁性和可扩展性。

## 项目概述

TickButcher是一个基于Python的开源量化交易框架，设计理念注重简洁性、性能和可扩展性。不同于重量级的量化平台，TickButcher采用轻量化架构，让用户能够快速构建和部署量化交易策略。

### 核心特性

- **轻量级架构**: 最小化的依赖和简洁的设计
- **高性能**: 基于事件驱动的架构，支持高频交易场景
- **模块化设计**: 松耦合的组件，便于定制和扩展
- **类型安全**: 完整的类型注解支持
- **易于使用**: 简洁的API设计，降低学习成本

## 系统架构

TickButcher采用分层架构设计：

```
┌─────────────────────────────────────┐
│            Strategy Layer           │  策略层
├─────────────────────────────────────┤
│            Engine Layer             │  引擎层 (AlphaHub)
├─────────────────────────────────────┤
│            Broker Layer             │  经纪商层
├─────────────────────────────────────┤
│            Data Layer               │  数据层
└─────────────────────────────────────┘
```

### 核心组件

#### AlphaHub (核心引擎)
- **职责**: 统一管理和协调所有组件
- **功能**: 
  - 策略管理和执行
  - 数据分发和处理
  - 订单路由和管理
  - 指标计算和缓存

#### Broker (经纪商抽象)
- **职责**: 提供统一的交易接口
- **功能**:
  - 订单提交和管理
  - 持仓跟踪
  - 账户管理
  - 事件通知

#### Strategy (策略框架)
- **职责**: 策略逻辑实现
- **功能**:
  - 信号生成
  - 风险控制
  - 仓位管理

#### CandleFeed (数据管理)
- **职责**: 行情数据处理
- **功能**:
  - 多时间框架支持
  - 实时数据更新
  - 历史数据查询

## 安装要求

- Python 3.13+
- pandas >= 2.3.2

### 可选依赖

```toml
[project.optional-dependencies]
sqlalchemy = ["sqlalchemy (>=2.0.43,<3.0.0)"]
asyncsqlchemy = ["sqlalchemy[asyncio] (>=2.0.43,<3.0.0)", "aiosqlite (>=0.21.0,<0.22.0)"]
matplotlib = ["matplotlib (>=3.10.6,<4.0.0)"]
httpx = ["httpx (>=0.28.1,<0.29.0)"]
```

## 快速开始

### 基本使用

```python
from tickbutcher import AlphaHub, Runnable
from tickbutcher.candlefeed import TimeframeType

# 创建Alpha引擎
hub = AlphaHub(timeframe_level=TimeframeType.M1)

# 添加数据源
# hub.add_kline(candleFeed=your_candle_feed)

# 添加策略
# hub.add_strategy(YourStrategy)

# 运行引擎
hub.run()
```

### 自定义策略

```python
from tickbutcher.strategys import CommonStrategy
from tickbutcher.order import OrderType, OrderSide

class MyStrategy(CommonStrategy):
    def next(self):
        # 获取最新价格数据
        current_candle = self.candled.get_current_candle(trading_pair)
        
        # 策略逻辑
        if self.should_buy():
            self.long_entry(
                trading_pair=trading_pair,
                quantity=100,
                order_type=OrderType.Market
            )
        elif self.should_sell():
            self.long_close(
                trading_pair=trading_pair,
                order_type=OrderType.Market
            )
```

## 项目结构

```
tickbutcher/
├── src/tickbutcher/
│   ├── __init__.py          # 核心导出
│   ├── alphahub.py          # 主引擎
│   ├── version.py           # 版本管理
│   ├── brokers/             # 经纪商模块
│   │   ├── common_broker.py
│   │   ├── account.py
│   │   └── ...
│   ├── strategys/           # 策略模块
│   │   ├── common_strategy.py
│   │   └── ...
│   ├── candlefeed/          # 数据模块
│   │   ├── candlefeed.py
│   │   └── ...
│   ├── Indicators/          # 指标模块
│   │   ├── ma.py
│   │   ├── mfi.py
│   │   └── ...
│   └── products/            # 金融产品定义
├── tests/                   # 测试代码
├── demo/                    # 示例代码
└── pyproject.toml          # 项目配置
```

## 设计理念

### 1. 简洁性优先
- 最小化的API设计
- 清晰的抽象层次
- 减少不必要的复杂性

### 2. 性能导向
- 事件驱动架构
- 内存优化的数据结构
- 高效的数据处理流程

### 3. 可扩展性
- 插件化的组件设计
- 标准化的接口定义
- 支持自定义扩展

### 4. 类型安全
- 完整的类型注解
- 编译时类型检查
- 更好的IDE支持

## 与vnpy的对比

| 特性 | TickButcher | vnpy |
|------|-------------|------|
| **设计理念** | 轻量化、简洁性 | 功能全面、企业级 |
| **学习曲线** | 平缓 | 陡峭 |
| **性能** | 高效、专注核心 | 功能丰富但相对重 |
| **扩展性** | 高度模块化 | 丰富的插件生态 |
| **适用场景** | 快速原型、个人交易 | 企业级、复杂策略 |
| **依赖管理** | 最小化依赖 | 完整的依赖栈 |

## 适用场景

- 个人量化交易者
- 策略快速原型开发
- 教学和研究
- 需要高度定制的场景
- 对性能有严格要求的应用

## 开发路线图

### v0.2.0 (规划中)
- [ ] 完善策略回测框架
- [ ] 添加更多技术指标
- [ ] 风险管理模块
- [ ] 数据库持久化支持

### v0.3.0 (规划中)
- [ ] 实时交易接口集成
- [ ] Web界面支持
- [ ] 性能监控和分析工具
- [ ] 多策略并行执行

## 贡献指南

我们欢迎各种形式的贡献：

1. 提交Bug报告和功能请求
2. 改进文档
3. 提交代码补丁
4. 分享使用经验

### 开发环境设置

```bash
# 克隆仓库
git clone <repository-url>
cd tickbutcher

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/
```

## 许可证

本项目采用MIT许可证 - 详见[LICENSE](LICENSE)文件。

## 联系方式

- 作者: ghostLostTheShell
- 邮箱: m18719301956@163.com
- 项目主页: [GitHub链接]

## 致谢

感谢vnpy项目为量化交易社区做出的贡献，TickButcher在设计中参考了vnpy的一些优秀思想，同时致力于提供更加轻量化的解决方案。