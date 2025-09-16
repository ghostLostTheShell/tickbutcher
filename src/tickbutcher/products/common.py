
from tickbutcher.products import AssetType, FinancialInstrument

# 加密货币
USDT = FinancialInstrument(symbol="USDT", type=AssetType.CRYPTO, precision=8)
BTC = FinancialInstrument(symbol="BTC", type=AssetType.CRYPTO, precision=8)
ETH = FinancialInstrument(symbol="ETH", type=AssetType.CRYPTO, precision=18)
SOL = FinancialInstrument(symbol="SOL", type=AssetType.CRYPTO, precision=9)

# 永续合约
BTCUSDT_P = FinancialInstrument(symbol="BTC/USDT@P", type=AssetType.PerpetualSwap, precision=8)
ETHUSDT_P = FinancialInstrument(symbol="ETH/USDT@P", type=AssetType.PerpetualSwap, precision=8)
SOLUSDT_P = FinancialInstrument(symbol="SOL/USDT@P", type=AssetType.PerpetualSwap, precision=9)

# 法币
CNY = FinancialInstrument(symbol="CNY", type=AssetType.FiatCurrency)
USD = FinancialInstrument(symbol="USD", type=AssetType.FiatCurrency)
JPY = FinancialInstrument(symbol="JPY", type=AssetType.FiatCurrency)
SGD = FinancialInstrument(symbol="SGD", type=AssetType.FiatCurrency)
GDB = FinancialInstrument(symbol="GDB", type=AssetType.FiatCurrency)
EUR = FinancialInstrument(symbol="EUR", type=AssetType.FiatCurrency)