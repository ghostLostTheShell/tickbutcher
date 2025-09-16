from tickbutcher.brokers.trading_pair import TradingPair
from tickbutcher.products import common as common_financial

# 现货交易对
BTCUSDT = TradingPair(
    base=common_financial.BTC,
    quote=common_financial.USDT,
    symbol="BTC/USDT",
    id="BTCUSDT",
    base_precision=8,
    quote_precision=8,
    baseCommissionPrecision=8,
    quoteCommissionPrecision=8
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
    base=common_financial.BTCUSDT_P,
    quote=common_financial.USDT,
    symbol="BTC/USDT@P",
    id="BTCUSDTP",
    base_precision=8,
    quote_precision=8,
    baseCommissionPrecision=8,
    quoteCommissionPrecision=8
)

ETHUSDTP = TradingPair(
    base=common_financial.ETHUSDT_P,
    quote=common_financial.USDT,
    symbol="ETH/USDT@P",
    id="ETHUSDTP",
    base_precision=8,
    quote_precision=8,
    baseCommissionPrecision=8,
    quoteCommissionPrecision=8
)

SOLUSDTP = TradingPair(
    base=common_financial.SOLUSDT_P,
    quote=common_financial.USDT,
    symbol="SOL/USDT@P",
    id="SOLUSDTP",
    base_precision=8,
    quote_precision=8,
    baseCommissionPrecision=8,
    quoteCommissionPrecision=8
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

