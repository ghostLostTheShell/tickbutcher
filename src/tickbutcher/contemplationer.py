from datetime import datetime
from tickbutcher.candlefeed import CandleFeedDB, CandleFeedProxy, TimeframeType
from tickbutcher.commission import Commission
from tickbutcher.products import FinancialInstrument
from pandas import DataFrame


class Contemplationer:
  
  
  def __init__(self):
    self.candle_feed_db = CandleFeedDB()
    self.candle_feed_proxy=CandleFeedProxy(self.candle_feed_db)

  def add_kline(self, *, kline:DataFrame, financial_type:FinancialInstrument, timeframe:TimeframeType, commission:Commission):
    self.candle_feed_db.add_kline(kline=kline, financial_type=financial_type, timeframe=timeframe, commission=commission)


  def run(self):
    self.time_interval = self.candle_feed_db.get_time_intervals()

    for current_time in self.time_interval:
      self.candle_feed_proxy.set_position(current_time)
      print(f"Current time: {datetime.fromtimestamp(current_time/1000)}")
