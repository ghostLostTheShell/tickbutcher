
import enum


class TimeframeType(enum.Enum):
  s1 = 0
  min1 = 1
  min5 = 2
  min15 = 3
  h1 = 4
  h4 = 5
  d1 = 6
  w1 = 7
  mo1 = 8
  y1 = 9

from .candlefeed import CandleFeed

__all__ = ['CandleFeed', 'TimeframeType']
# class CandleFeedDB:
#     klines: List[DataFrame]
#     financial_type_tble:Dict[FinancialInstrument, TimeframeDict]
#     commission_tble: Dict[FinancialInstrument, Commission]

#     def __init__(self):
#       self.klines = []
#       self.financial_type_tble = {}
#       self.commission_tble = {}

#     def add_kline(self, *, kline: DataFrame, financial_type: FinancialInstrument, timeframe: TimeframeType, commission: Commission):
#       #根据时间周期将K线数据添加到相应的字典中
#       if financial_type not in self.financial_type_tble:
#           self.financial_type_tble[financial_type] = TimeframeDict(
#               m1=None,
#               m5=None,
#               m15=None,
#               h1=None,
#               h4=None,
#               d1=None,
#               w1=None
#           )

#       self.financial_type_tble[financial_type][timeframe.value] = kline

#       self.klines.append(kline)
#       self.financial_type_tble[financial_type][timeframe.value] = kline
#       self.commission_tble[financial_type] = commission

#     def get_klines(self):
#       return self.klines

#     def get_time_intervals(self):
      
#       current = None
      
#       for kline in self.klines:
#         if current is None:
#           current = kline.index
#           continue
#         else:
#           current = current.union(kline.index)
          
#       return current

#     def get_commission(self, financial_type: FinancialInstrument):
#       return self.commission_tble[financial_type]

# class CandleFeedProxy:
#     position: int
#     dataframe: DataFrame
#     timeframe: str
    
#     def __init__(self, db: CandleFeedDB):
#         self.db = db

#     def set_position(self, position: int):
#       self.position = position
#       return self

#     def __getattr__(self, name: str):
#       # bct_m15[-1]
#       financial_type_id, timeframe = name.split("_")
#       self.timeframe = timeframe
      
#       for financial_type in self.db.financial_type_tble.keys():
#         if financial_type.id == financial_type_id:
#           self.dataframe = self.db.financial_type_tble[financial_type].get(timeframe)
          
#       return self
    
#     def __getitem__(self, key):
#       if self.dataframe is None:
#         return None
#       else:
        
#         if self.position not in self.dataframe.index:
#           return None
        
#         if key == 0:

#           return self.dataframe.loc[self.position]

#         elif key > 0:
#           raise IndexError("Index out of range")
#         else:
#           i = self.dataframe.index.get_loc(self.position)
          
          
          
#           if i + key < 0:
#             raise IndexError("Index out of range")
#           i = i + key
          
#           return self.dataframe.iloc[i + key]

#     def __setitem__(self, key, value):
#         pass

#     def __delitem__(self, key):
#         pass
      

  
