
from enum import Enum
from typing import Dict, List, TypeVar

class AssetType(Enum):
  STOCK = 1 #股票
  BOND = 2 #债券
  FUTURE = 3 #期货
  CRYPTO = 4 #加密货币
  PerpetualSwap = 5 #永续合约
  FiatCurrency = 6 #法币

B = TypeVar("B", bound="FinancialInstrument")

class FinancialInstrument():
  """概况所有可交易资产"""
  """
    String     symbol  标的
    AssetType  type    市场产品种类 
  """
  __all__symbol_instances_table:Dict[str, B] = {}
  
  symbol:str
  type:AssetType

  def __new__(cls, *args, **kwargs) -> B:
    symbol = kwargs.get("symbol")
    asset_type = kwargs.get("type")
    if symbol not in cls.__all__symbol_instances_table.keys():
        # 如果没有实例，则创建一个新的并存储到字典中
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs) 
        cls.__all__symbol_instances_table[symbol] = instance

    instance = cls.__all__symbol_instances_table[symbol]
    if instance.type is not asset_type:
        raise ValueError(f"Symbol '{symbol}' is already registered with a different type.")

    return cls.__all__symbol_instances_table[symbol]

  def __init__(self, *, symbol: str, type: AssetType) -> object:
    self.symbol = symbol
    self.type = type
