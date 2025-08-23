from datetime import datetime
from tickbutcher.candlefeed import CandleFeedDB, TimeframeType
from tickbutcher.products import FinancialInstrument
from pandas import DataFrame


class Contemplationer:
  
  
  def __init__(self):
    self.candle_feed_db = CandleFeedDB()
    pass

  def add_kline(self, *, kline:DataFrame, financial_type:FinancialInstrument, timeframe:TimeframeType):
    self.candle_feed_db.add_kline(kline=kline, financial_type=financial_type, timeframe=timeframe)


  def run(self):
    self.time_interval = self.candle_feed_db.get_time_intervals()

    for current_time in self.time_interval:
      print(f"Current time: {datetime.fromtimestamp(current_time/1000)}")
