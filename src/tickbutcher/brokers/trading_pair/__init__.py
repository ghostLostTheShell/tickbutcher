from typing import Dict, TypeVar, Any
from tickbutcher.products import FinancialInstrument
import re


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
  def get_trading_pair(cls, id: str, normalize: bool = True) -> 'TradingPair':
    """
    根据ID获取交易对实例，支持特殊符号处理
    
    Args:
        id: 交易对ID
        normalize: 是否对ID进行标准化处理，默认为True
        
    Returns:
        TradingPair: 交易对实例
        
    Raises:
        ValueError: 当交易对不存在或ID格式无效时
        TypeError: 当参数类型错误时
    """
    if not id or not id.strip():
      raise ValueError("交易对ID不能为空")
    
    # 清理输入
    original_id = id
    id = id.strip()
    
    # 如果需要标准化，处理特殊符号
    if normalize:
      id = cls._normalize_trading_pair_id(id)
    
    # 获取实例
    instance = cls.__instances.get(id)
    if not instance:
      # 如果标准化后仍未找到，尝试不标准化的原始ID
      if normalize and original_id.strip() != id:
        instance = cls.__instances.get(original_id.strip())
      
      if not instance:
        # 提供更详细的错误信息，列出可用的交易对
        available_ids = ', '.join(sorted(cls.__instances.keys())[:5])
        if len(cls.__instances) > 5:
          available_ids += f"... (共 {len(cls.__instances)} 个)"
        raise ValueError(
          f"交易对 '{original_id}' 不存在。"
          f"可用的交易对: {available_ids}"
        )
    
    return instance
  
  @classmethod
  def _normalize_trading_pair_id(cls, id: str) -> str:
    """
    标准化交易对ID，处理特殊符号
    
    支持的转换规则:
    - 移除空格: "BTC USDT" -> "BTCUSDT"
    - 移除斜杠: "BTC/USDT" -> "BTCUSDT"
    - 移除连字符: "BTC-USDT" -> "BTCUSDT"
    - 移除下划线: "BTC_USDT" -> "BTCUSDT"
    - 统一大写: "btcusdt" -> "BTCUSDT"
    - 永续合约符号处理: "BTC/USDT@P" -> "BTCUSDTP", "BTCUSDT-PERP" -> "BTCUSDTP"
    
    Args:
        id: 原始交易对ID
        
    Returns:
        str: 标准化后的交易对ID
    """
    # 统一大写
    normalized = id.upper()
    
    # 处理永续合约的特殊标记
    # BTC/USDT@P -> BTCUSDTP
    # BTCUSDT-PERP -> BTCUSDTP
    # BTCUSDT_PERP -> BTCUSDTP
    normalized = re.sub(r'@P$', 'P', normalized)
    normalized = re.sub(r'[-_]PERP$', 'P', normalized)
    normalized = re.sub(r'[-_]PERPETUAL$', 'P', normalized)
    
    # 移除常见分隔符
    normalized = normalized.replace('/', '')
    normalized = normalized.replace('-', '')
    normalized = normalized.replace('_', '')
    normalized = normalized.replace(' ', '')
    normalized = normalized.replace('.', '')
    
    # 验证结果只包含字母数字字符
    if not normalized.isalnum():
      raise ValueError(
        f"标准化后的交易对ID包含无效字符: '{normalized}' "
        f"(原始: '{id}')"
      )
    
    return normalized
  
  @classmethod
  def exists(cls, id: str, normalize: bool = True) -> bool:
    """
    检查交易对是否存在
    
    Args:
        id: 交易对ID
        normalize: 是否对ID进行标准化处理
        
    Returns:
        bool: 存在返回True，否则返回False
    """
    try:
      cls.get_trading_pair(id, normalize=normalize)
      return True
    except (ValueError, TypeError):
      return False
  
  @classmethod
  def get_all_trading_pairs(cls) -> Dict[str, 'TradingPair']:
    """
    获取所有已注册的交易对
    
    Returns:
        Dict[str, TradingPair]: 交易对ID到实例的映射字典
    """
    return cls.__instances.copy()
  
  @classmethod
  def get_trading_pair_ids(cls) -> list[str]:
    """
    获取所有交易对ID列表
    
    Returns:
        list[str]: 交易对ID列表
    """
    return list(cls.__instances.keys())
