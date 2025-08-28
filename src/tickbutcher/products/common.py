
from tickbutcher.products import AssetType, AssetType, FinancialInstrument

# 加密货币
USDT = FinancialInstrument("USDT", AssetType.CRYPTO)
BTC = FinancialInstrument("BTC", AssetType.CRYPTO)
ETH = FinancialInstrument("ETH", AssetType.CRYPTO)
SOL = FinancialInstrument("SOL", AssetType.CRYPTO)

# 永续合约
BTCUSDT_P = FinancialInstrument("BTC/USDT@p", AssetType.PerpetualSwap)
ETHUSDT_P = FinancialInstrument("ETH/USDT@p", AssetType.PerpetualSwap)
SOLUSDT_P = FinancialInstrument("SOL/USDT@p", AssetType.PerpetualSwap)

# 法币
CNY = FinancialInstrument("CNY", AssetType.FiatCurrency)
USD = FinancialInstrument("USD", AssetType.FiatCurrency)
JPY = FinancialInstrument("JPY", AssetType.FiatCurrency)
SGD = FinancialInstrument("SGD", AssetType.FiatCurrency)
GDB = FinancialInstrument("GDB", AssetType.FiatCurrency)
EUR = FinancialInstrument("EUR", AssetType.FiatCurrency)