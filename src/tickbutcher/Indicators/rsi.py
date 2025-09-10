
from tickbutcher.Indicators import Indicator


class RelativeStrengthIndex(Indicator):
    def __init__(self, data, period=14):
        self.data = data
        self.period = period

    def calculate(self):
        # Implementation for calculating RSI
        pass