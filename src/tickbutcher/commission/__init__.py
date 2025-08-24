from abc import ABC, abstractmethod

class Commission(ABC):
    """抽象基类：定义手续费计算接口"""
    
    @abstractmethod
    def calculate(self, price: float, quantity: float) -> float:
        """
        计算手续费
        :param price: 成交价格
        :param quantity: 成交数量
        :return: 手续费金额
        """
        pass


class FixedRateCommission(Commission):
    """按成交金额比例收取手续费（常见方式，比如 0.1%）"""
    
    def __init__(self, rate: float):
        """
        :param rate: 手续费率，比如 0.001 = 0.1%
        """
        self.rate = rate
    
    def calculate(self, price: float, quantity: float) -> float:
        return price * quantity * self.rate


class FixedPerTradeCommission(Commission):
    """每笔交易收固定金额手续费"""
    
    def __init__(self, fee: float):
        """
        :param fee: 固定手续费，比如 5 USDT
        """
        self.fee = fee
    
    def calculate(self, price: float, quantity: float) -> float:
        return self.fee


class TieredCommission(Commission):
    """分级费率，比如 VIP 用户手续费更低"""
    
    def __init__(self, tiers: dict):
        """
        :param tiers: 字典 {交易额阈值: 手续费率}
                      例如 {10000: 0.001, 50000: 0.0008, float("inf"): 0.0005}
        """
        self.tiers = dict(sorted(tiers.items()))
    
    def calculate(self, price: float, quantity: float) -> float:
        amount = price * quantity
        for threshold, rate in self.tiers.items():
            if amount <= threshold:
                return amount * rate
        return amount * list(self.tiers.values())[-1]


class MakerTakerCommission(Commission):
    """区分挂单和吃单手续费"""
    
    def __init__(self, maker_rate: float, taker_rate: float):
        """
        :param maker_rate: 挂单手续费率
        :param taker_rate: 吃单手续费率
        """
        self.maker_rate = maker_rate
        self.taker_rate = taker_rate
    
    def calculate(self, price: float, quantity: float, is_taker: bool = True) -> float:
        rate = self.taker_rate if is_taker else self.maker_rate
        return price * quantity * rate
