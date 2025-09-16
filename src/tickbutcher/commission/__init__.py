from abc import ABC, abstractmethod
import enum

class CommissionType(enum.Enum):
  """_summary_

  OnQuote后缀 义为基于交易对的报价货币统一收取，否则按交易所得物进行
  """
  FixedPerTrade = 0
  FixedRate = 1
  Tiered = 2
  Maker = 3
  Taker = 4

class Commission(ABC):
  """抽象基类：定义手续费计算接口"""

  @abstractmethod
  def calculate(self, value:float) -> float:
        """
        计算手续费
        :param value: 成交金额
        :return: 手续费金额
        """
        pass

class FixedRateCommission(Commission):
  """按成交金额比例收取手续费（常见方式，比如 0.1%）"""

  def __init__(self, rate: int,):
      """
      :param rate: 手续费率，(万分之几) 比如 0.001 = 0.1%
      :param c_type: 只能为 CommissionType.FixedRate 或 CommissionType.FixedRateOnQuote
      """
      self.rate = rate

  def calculate(self, value:float) -> float:
      return value * self.rate

class FixedPerTradeCommission(Commission):
  """每笔交易收固定金额手续费"""
  commission_type = CommissionType.FixedPerTrade

  def __init__(self, fee: int):
      """
      :param fee: 固定手续费，比如 5 USDT
      """
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

class MakerCommission(Commission):
  """区分挂单和吃单手续费
  """

  def __init__(self, maker_rate: int):
    """
    :param maker_rate: 挂单手续费率(万分之几)
    """
    self.maker_rate = maker_rate

  def calculate(self, value:float) -> float:
    return (value * self.maker_rate) / 10000


class TakerCommission(Commission):
  """吃单手续费"""
  def __init__(self, taker_rate: int):
    """
    :param taker_rate: 吃单手续费率(万分之几)
    """
    self.taker_rate = taker_rate
    self.commission_type = CommissionType.Taker

  def calculate(self, value:float) -> float:
    return (value * self.taker_rate) / 10000