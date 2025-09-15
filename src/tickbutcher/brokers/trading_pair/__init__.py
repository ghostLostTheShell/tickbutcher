from typing import Dict, TypeVar, Any
from tickbutcher.products import FinancialInstrument


B = TypeVar("B", bound="TradingPair")
class TradingPair():
  base:FinancialInstrument    #基础货币
  quote:FinancialInstrument   #计价货币
  symbol:str                  # 交易对符号，如 BTC/USDT
  id:str                      # 交易对ID
  base_precision: int         # 基础货币的小数精度（如 BTC 为 2）
  quote_precision: int        # 计价货币的小数精度（如 USDT 为 2）
  baseCommissionPrecision:int = 8  #基础货币手续费精度
  quoteCommissionPrecision:int = 8 #计价货币手续费精度
  
  __instances: Dict[str, 'TradingPair'] = {}

  #每次创建新实例时，把实例根据id保存起来
  def __new__(cls,
              *args: Any, 
              **kwargs: Any) -> 'TradingPair':
    id:str = kwargs.get("id")     # type: ignore
    base:FinancialInstrument = kwargs.get("base")     # type: ignore
    quote:FinancialInstrument = kwargs.get("quote")   # type: ignore
    symbol:str = kwargs.get("symbol") # type: ignore
    # base_precision:int = kwargs.get("base_precision", 2) # type: ignore
    # base_amount_precision:int = kwargs.get("base_amount_precision", 2) # type: ignore

    if id not in cls.__instances.keys():
      # 如果没有实例，则创建一个新的并存储到字典中
      instance = super().__new__(cls)
      instance.__init__(*args, **kwargs)
      cls.__instances[id] = instance

    #判断kwargs里面参数是否实例的属性一致
    
    instance = cls.__instances[id]
      
    if (instance.base != base
        or instance.quote != quote
        or instance.symbol != symbol 
        # or instance.base_precision != base_precision
        # or instance.base_amount_precision != base_amount_precision
        ):
        raise ValueError(f"TradingPair with id {id} already exists with different parameters.")

    return cls.__instances[id]
    
  def __init__(self, *, 
                base: FinancialInstrument, 
                quote: FinancialInstrument,
                symbol: str,
                id: str,
                base_precision: int=1,
                quote_precision: int=1,
                baseCommissionPrecision: int=1,
                quoteCommissionPrecision: int=1
               ):
      self.base = base
      self.quote = quote
      self.symbol = symbol
      self.id = id
      self.base_precision = base_precision
      self.quote_precision = quote_precision
      self.baseCommissionPrecision = baseCommissionPrecision
      self.quoteCommissionPrecision = quoteCommissionPrecision



  @classmethod
  def get_trading_pair(cls, id: str) -> 'TradingPair':
    instance = cls.__instances.get(id)
    if not instance:
      raise ValueError(f"TradingPair with id {id} does not exist.")
    return instance
