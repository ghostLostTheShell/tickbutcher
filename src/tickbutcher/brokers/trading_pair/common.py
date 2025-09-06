from tickbutcher.brokers.trading_pair import TradingPair
from tickbutcher.products import common as common_financial

# 现货交易对
BTCUSDT = TradingPair(
    base=common_financial.BTC,
    quote=common_financial.USDT,
    symbol="BTC/USDT",
    id="BTCUSDT",
    base_amount_precision=7,
    base_precision=1
)

ETHUSDT = TradingPair(
    base=common_financial.ETH,
    quote=common_financial.USDT,
    symbol="ETH/USDT",
    id="ETHUSDT",
)

SOLUSDT = TradingPair(
    base=common_financial.SOL,
    quote=common_financial.USDT,
    symbol="SOL/USDT",
    id="SOLUSDT"
)


# 永续合约交易对
BTCUSDTP = TradingPair(
    base=common_financial.BTC,
    quote=common_financial.USDT,
    symbol="BTC/USDT@p",
    id="BTCUSDTP",
    base_amount_precision=7,
    base_precision=1
)

ETHUSDTP = TradingPair(
    base=common_financial.ETH,
    quote=common_financial.USDT,
    symbol="ETH/USDT@p",
    id="ETHUSDTP",
    base_amount_precision=7,
    base_precision=1
)

SOLUSDTP = TradingPair(
    base=common_financial.SOL,
    quote=common_financial.USDT,
    symbol="SOL/USDT@p",
    id="SOLUSDTP",
    base_amount_precision=2,
    base_precision=2
)

# 法币对
USDJPY = TradingPair(
    base=common_financial.USD,
    quote=common_financial.JPY,
    symbol="USD/JPY",
    id="USDJPY"
)

USDCNY = TradingPair(
    base=common_financial.USD,
    quote=common_financial.CNY,
    symbol="USD/CNY",
    id="USDCNY"
)

EURUSD = TradingPair(
    base=common_financial.EUR,
    quote=common_financial.USD,
    symbol="EUR/USD",
    id="EURUSD"
)

