
from enum import Enum

class AssetType(Enum):
  STOCK = 1 #股票
  BOND = 2 #债券
  FUTURE = 3 #期货
  CRYPTO = 4 #加密货币
  PerpetualSwap = 5 #永续合约

class FinancialInstrument():
  """概况所有可交易资产"""

  def __init__(self, symbol:str, name:str, type:AssetType):
      self.symbol = symbol
      self.name = name
      self.type = type
