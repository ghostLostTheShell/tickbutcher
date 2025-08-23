
from typing import Dict, List
from tickbutcher.products import FinancialInstrument
from pandas import DataFrame

class Contemplationer:
  
  financial_type_tble:Dict[DataFrame, FinancialInstrument] = {}
  time_interval:List[int]=[]
  klines:List[DataFrame]=[] 
  
  def __init__(self):
    pass

  def add_klines(self, data:DataFrame, financial_type:FinancialInstrument):
    self.financial_type_tble[data] = financial_type
    self.klines=data
    

  
  def int_time_interval(self):
    """根据 klines 初始化 time_interval"""
    self.time_interval = [i for i in range(len(self.klines))]

  def run(self):

    for scale in self.time_interval:
      print(f"Contemplating {scale}")
