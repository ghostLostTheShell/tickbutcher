from typing import Dict, TypeVar
from tickbutcher.products import FinancialInstrument


B = TypeVar("B", bound="TradingPair")
class TradingPair():
  base:FinancialInstrument  #基础货币
  quote:FinancialInstrument #计价货币
  symbol:str                # 交易对符号，如 BTC/USDT
  id:str                    # 交易对ID

  __instances: Dict[str, B] = {}

  #每次创建新实例时，把实例根据id保存起来
  def __new__(cls,*args, **kwargs) -> B:
    id = kwargs.get("id")
    base = kwargs.get("base")
    quote = kwargs.get("quote")
    symbol = kwargs.get("symbol")
    
    if id not in cls.__instances.keys():
      # 如果没有实例，则创建一个新的并存储到字典中
      instance = super().__new__(cls)
      instance.__init__(*args, **kwargs)
      cls.__instances[id] = instance

    #判断kwargs里面参数是否实例的属性一致
    
    instance = cls.__instances[id]
    if (instance.base != base or
        instance.quote != quote or
        instance.symbol != symbol):
        raise ValueError(f"TradingPair with id {id} already exists with different parameters.")

    return cls.__instances[id]
    
  def __init__(self, *, 
               base: FinancialInstrument, 
               quote: FinancialInstrument,
               symbol: str,
               id: str) -> object:
      self.base = base
      self.quote = quote
      self.symbol = symbol
      self.id = id


  @classmethod
  def get_trading_pair(cls, id: str) -> 'TradingPair':
    instance = cls.__instances.get(id)
    if not instance:
      raise ValueError(f"TradingPair with id {id} does not exist.")
    return instance
