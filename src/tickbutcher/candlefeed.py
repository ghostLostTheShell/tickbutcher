import enum
from typing import Dict, List, TypedDict
from pandas import DataFrame
from tickbutcher.commission import Commission
from tickbutcher.products import FinancialInstrument

class TimeframeType(enum.Enum):
  M1 = "m1"
  M5 = "m5"
  M15 = "m15"
  H1 = "h1"
  H4 = "h4"
  D1 = "d1"
  W1 = "w1"

class TimeframeDict(TypedDict):
    m1:   DataFrame
    m5:   DataFrame
    m15:  DataFrame
    h1:   DataFrame
    h4:   DataFrame
    d1:   DataFrame
    w1:   DataFrame




class CandleFeedDB:
    klines: List[DataFrame]
    financial_type_tble:Dict[FinancialInstrument, TimeframeDict]
    commission_tble: Dict[FinancialInstrument, Commission]

    def __init__(self):
      self.klines = []
      self.financial_type_tble = {}
      self.commission_tble = {}

    def add_kline(self, *, kline: DataFrame, financial_type: FinancialInstrument, timeframe: TimeframeType, commission: Commission):
      #根据时间周期将K线数据添加到相应的字典中
      if financial_type not in self.financial_type_tble:
          self.financial_type_tble[financial_type] = TimeframeDict(
              m1=None,
              m5=None,
              m15=None,
              h1=None,
              h4=None,
              d1=None,
              w1=None
          )

      self.financial_type_tble[financial_type][timeframe.value] = kline

      self.klines.append(kline)
      self.financial_type_tble[financial_type][timeframe.value] = kline
      self.commission_tble[financial_type] = commission

    def get_klines(self):
      return self.klines

    def get_time_intervals(self):
      
      current = None
      
      for kline in self.klines:
        if current is None:
          current = kline.index
          continue
        else:
          current = current.union(kline.index)
          
      return current

    def get_commission(self, financial_type: FinancialInstrument):
      return self.commission_tble[financial_type]

class CandleFeedProxy:
    position: int
    dataframe: DataFrame
    
    def __init__(self, db: CandleFeedDB):
        self.db = db

    def set_position(self, position: int):
      self.position = position
      return self

    def __getattr__(self, name: str):
      # bct_m15[-1]
      financial_type_id, timeframe = name.split("_")
      
      for financial_type in self.db.financial_type_tble.keys():
        if financial_type.id == financial_type_id:
          self.dataframe = self.db.financial_type_tble[financial_type].get(timeframe)
          
      return self
    
    def __getitem__(self, key):
      if self.dataframe is None:
        return None
      else:
        if key == 0:
          return self.dataframe.loc[self.position]
        
        elif key > 0:          
          raise IndexError("Index out of range")
        else:
          i = self.dataframe.index.get_loc(self.position)
          if i + key < 0:
            raise IndexError("Index out of range")
          
          return self.dataframe.iloc[i + key]

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass