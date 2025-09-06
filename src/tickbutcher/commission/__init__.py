from abc import ABC, abstractmethod
import enum
from typing import Literal, Optional, TypeAlias

class CommissionType(enum.Enum):
  """_summary_

  OnQuote后缀 义为基于交易对的报价货币统一收取，否则按交易所得物进行
  """
  FixedPerTrade = 0
  FixedPerTradeOnQuote = 1
  FixedRate = 2
  FixedRateOnQuote=3
  Tiered = 4
  FixedOnQuote =5 
  MakerTaker = 6
  MakerTakerOnQuote =5 

class Commission(ABC):
  """抽象基类：定义手续费计算接口"""

  commission_type: CommissionType

  @abstractmethod
  def calculate(self, value:float) -> float:
        """
        计算手续费
        :param value: 成交金额
        :return: 手续费金额
        """
        pass

CommissionRateType: TypeAlias = Optional[Literal[
      CommissionType.FixedRate,
      CommissionType.FixedRateOnQuote
  ]]
class FixedRateCommission(Commission):
  """按成交金额比例收取手续费（常见方式，比如 0.1%）"""


  def __init__(self, rate: int, *,
               c_type: CommissionRateType = CommissionType.FixedRate):
      """
      :param rate: 手续费率，(万分之几) 比如 0.001 = 0.1%
      :param c_type: 只能为 CommissionType.FixedRate 或 CommissionType.FixedRateOnQuote
      """
      if c_type not in (CommissionType.FixedRate, CommissionType.FixedRateOnQuote):
          raise ValueError("c_type must be FixedRate or FixedRateOnQuote")
      self.rate = rate
      self.commission_type = c_type


  def calculate(self, value:float) -> float:
      return value * self.rate


CommissionFixedPerTradeType: TypeAlias = Optional[Literal[
      CommissionType.FixedPerTrade,
      CommissionType.FixedPerTradeOnQuote
  ]]
class FixedPerTradeCommission(Commission):
  """每笔交易收固定金额手续费"""
  commission_type = CommissionType.FixedPerTrade

  def __init__(self, fee: int, *, c_type:CommissionFixedPerTradeType=CommissionType.FixedPerTrade):
      """
      :param fee: 固定手续费，比如 5 USDT
      :param c_type: 只能为 CommissionType.FixedPerTrade 或 CommissionType.FixedPerTradeOnQuote
      """
      if c_type not in (CommissionType.FixedPerTrade, CommissionType.FixedPerTradeOnQuote):
          raise ValueError("c_type must be FixedPerTrade or FixedPerTradeOnQuote")
      self.commission_type = c_type
      self.fee = fee

  def calculate(self, value:float) -> int:
      return self.fee

class TieredCommission(Commission):
  """分级费率，比如 VIP 用户手续费更低"""
  def __init__(self, tiers: list[tuple[float, float]]):
    """
    :param tiers: 分级费率列表，每个元素为 (金额上限, 费率)，按金额从小到大排列。
            例如：[(1000, 0.001), (5000, 0.0008), (float('inf'), 0.0005)]
    """
    if not tiers or any(len(t) != 2 for t in tiers):
      raise ValueError("tiers must be a list of (amount, rate) tuples")
    self.tiers = sorted(tiers, key=lambda x: x[0])
    self.commission_type = CommissionType.Tiered

  def calculate(self, value:float) -> float:
    for amount, rate in self.tiers:
      if value <= amount:
        return (value * rate) / 10000
    # fallback, should not reach here if tiers are set correctly
    return (value * self.tiers[-1][1]) / 10000


CommissionMakerTakerType: TypeAlias = Optional[Literal[
  CommissionType.MakerTaker,
  CommissionType.MakerTakerOnQuote
]]
class MakerTakerCommission(Commission):
  """区分挂单和吃单手续费
  """

  def __init__(self, 
                maker_rate: int, 
                taker_rate: int, 
                *,
                c_type:CommissionMakerTakerType=CommissionType.MakerTaker
                ):
    """
    :param maker_rate: 挂单手续费率(万分之几)
    :param taker_rate: 吃单手续费率(万分之几)
    :param c_type: 只能为 CommissionType.MakerTaker 或 CommissionType.MakerTakerOnQuote
    """
    if c_type not in [CommissionType.MakerTaker, CommissionType.MakerTakerOnQuote]:
      raise ValueError("c_type must be CommissionType.MakerTaker or CommissionType.MakerTakerOnQuote")
    
    self.commission_type = c_type
    self.maker_rate = maker_rate
    self.taker_rate = taker_rate



  def calculate(self, value:float, is_taker: bool = True) -> float:
    rate = self.taker_rate if is_taker else self.maker_rate
    return (value * rate) / 10000
