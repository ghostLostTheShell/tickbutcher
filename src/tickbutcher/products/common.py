
from tickbutcher.products import AssetType, FinancialInstrument

# 加密货币
USDT = FinancialInstrument(symbol="USDT", type=AssetType.CRYPTO, precision=8)
BTC = FinancialInstrument(symbol="BTC", type=AssetType.CRYPTO)
ETH = FinancialInstrument(symbol="ETH", type=AssetType.CRYPTO)
SOL = FinancialInstrument(symbol="SOL", type=AssetType.CRYPTO)

# 永续合约
BTCUSDT_P = FinancialInstrument(symbol="BTC/USDT@P", type=AssetType.PerpetualSwap)
ETHUSDT_P = FinancialInstrument(symbol="ETH/USDT@P", type=AssetType.PerpetualSwap)
SOLUSDT_P = FinancialInstrument(symbol="SOL/USDT@P", type=AssetType.PerpetualSwap)

# 法币
CNY = FinancialInstrument(symbol="CNY", type=AssetType.FiatCurrency)
USD = FinancialInstrument(symbol="USD", type=AssetType.FiatCurrency)
JPY = FinancialInstrument(symbol="JPY", type=AssetType.FiatCurrency)
SGD = FinancialInstrument(symbol="SGD", type=AssetType.FiatCurrency)
GDB = FinancialInstrument(symbol="GDB", type=AssetType.FiatCurrency)
EUR = FinancialInstrument(symbol="EUR", type=AssetType.FiatCurrency)