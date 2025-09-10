"""Moving Average Indicators"""

from tickbutcher.Indicators import Indicator


class SimpleMovingAverage(Indicator):
    def __init__(self, period: int):
        self.period = period
        self.prices = []

    def add_price(self, price: float):
        self.prices.append(price)
        if len(self.prices) > self.period:
            self.prices.pop(0)

    def get_average(self) -> float:
        if not self.prices:
            return 0.0
        return sum(self.prices) / len(self.prices)
      
class ExponentialMovingAverage(Indicator):
    def __init__(self, period: int):
        self.period = period
        self.multiplier = 2 / (period + 1)
        self.ema = None

    def add_price(self, price: float):
        if self.ema is None:
            self.ema = price
        else:
            self.ema = (price - self.ema) * self.multiplier + self.ema

    def get_average(self) -> float:
        return self.ema if self.ema is not None else 0.0
      
class WeightedMovingAverage(Indicator):
    def __init__(self, period: int):
        self.period = period
        self.prices = []

    def add_price(self, price: float):
        self.prices.append(price)
        if len(self.prices) > self.period:
            self.prices.pop(0)

    def get_average(self) -> float:
        if not self.prices:
            return 0.0
        weights = list(range(1, len(self.prices) + 1))
        weighted_sum = sum(p * w for p, w in zip(self.prices, weights))
        return weighted_sum / sum(weights)