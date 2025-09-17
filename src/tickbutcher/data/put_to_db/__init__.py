
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import enum
import httpx
from typing import Any, Dict, List, Optional,Tuple



class TimeframeType(enum.Enum):
  sec1 = 0
  min1 = 1
  min5 = 2
  min15 = 3
  h1 = 4
  h4 = 5
  d1 = 6
  w1 = 7
  mo1 = 8
  y1 = 9


OHLC = Tuple[int, float, float, float, float, float]

class Exchange(ABC):
  @abstractmethod
  async def fetch_ohlcv(self, symbol:str, timeframe:TimeframeType, start_time:datetime, limit:int)->List[OHLC]: ...

class Binance(Exchange):
  """
  symbol 规则 BTC/USDT 表示现货, BTC/USDT@p
  """

  def __init__(self):
    self.spot_base_url = "https://api.binance.com/api/v3"
    self.ps_base_url = "https://fapi.binance.com/fapi/v1"
    self.session = httpx.AsyncClient()

  def norm_symbol(self, symbol: str):
    if self.is_perpetual_swap(symbol):
      return symbol.replace("@P", "").replace("/", "")
    else:
      return symbol.replace("/", "")
    
  def is_perpetual_swap(self, symbol: str):
    if "@P" in symbol:
      return True
    
    return False

  async def exchange_info(self, symbol:Optional[str]=None, symbols:Optional[List[str]]=None):    
    if symbol and self.is_perpetual_swap(symbol):
      url = f"{self.ps_base_url}/exchangeInfo"
    else:
      url = f"{self.spot_base_url}/exchangeInfo"
    if symbol is not None:
      symbol = self.norm_symbol(symbol)
    if symbols is not None:
      symbols = [self.norm_symbol(s) for s in symbols]
    
    params:Dict[str, Any] = {}
    if symbol is not None:
      params['symbol'] = symbol
      
    if symbols is not None:
      params['symbols'] = symbols
      
    response = await self.session.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Error fetching data: {response.text}")
    data = response.json()
    return data
    
  
  async def fetch_ohlcv(self, symbol:str, timeframe:str, start_time:int, end_time:int, limit:int=500 ): # type: ignore
    url = f"{self.spot_base_url}/klines"
    if self.is_perpetual_swap(symbol):
      url = f"{self.ps_base_url}/klines"
    else:
      url = f"{self.spot_base_url}/klines"  
      
    symbol = self.norm_symbol(symbol)
    
    
    params = {
        "symbol": symbol,
        "interval": timeframe,
        "startTime": start_time,
        # "endTime": end_time,
        "limit": limit
    }
    response = await self.session.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Error fetching data: {response.text}")
    data = response.json()
    return data
  

class PolygonEx(Exchange):
  """
  拉取股票数据
  """

  def __init__(self, all_stock: str, candle_url: str, api_key: Optional[str]=None):
    self.all_stock = all_stock
    self.candle_url = candle_url
    self.session = httpx.AsyncClient()
    self.api_key = api_key



  async def fetch_ohlcv(self, symbol:str, timeframe:TimeframeType, start_time:datetime, limit:int):

    symbol = symbol.split("/")[0]  # 去掉股票代码中的市场后缀，如 "AAPL/USD" -> "AAPL"
    end_time:datetime

    _timeframe:str
    _s:int= int(start_time.timestamp() * 1000)
    _e:int=0
    match timeframe:
      case TimeframeType.sec1:
        _timeframe = "1/second"
        end_time = start_time + timedelta(seconds=limit)
        
      case TimeframeType.min1:
        _timeframe = "1/minute"
        end_time = start_time + timedelta(minutes=limit)
      case TimeframeType.min5:
        _timeframe = "5/minute"
        end_time = start_time + timedelta(minutes=5*limit)
      case TimeframeType.min15:
        _timeframe = "15/minute"
        end_time = start_time + timedelta(minutes=15*limit)
      case TimeframeType.h1:
        _timeframe = "1/hour"
        end_time = start_time + timedelta(hours=limit)
      case TimeframeType.h4:
        _timeframe = "4/hour"
        end_time = start_time + timedelta(hours=4*limit)
      case TimeframeType.d1:
        _timeframe = "1/day"
        end_time = start_time + timedelta(days=limit)
      case TimeframeType.w1:
        raise  Exception("mo1Not implemented yet")
        # _timeframe = "1Week"
        # end_time = start_time + timedelta(weeks=limit)
      case TimeframeType.mo1:
        raise  Exception("mo1Not implemented yet")
        # _timeframe = "1Month"
        # end_time = start_time + timedelta(days=30*limit)
      case TimeframeType.y1:
        raise  Exception("y1Not implemented yet")
        _timeframe = "1Year"
      case _:
        raise ValueError(f"Invalid timeframe: {timeframe}") 
    _e = int(end_time.timestamp() * 1000)
    url = f"{self.candle_url}aggs/ticker/{symbol}/range/{_timeframe}/{_s}/{_e}"
    params = {
        "adjusted": "true",
        "sort": "asc",
        "apiKey": self.api_key,
        "limit": limit
    }
    response = await self.session.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Error fetching data: {response.text}")
    data = response.json()


    data = [(item['t'], item['o'], item['h'], item['l'], item['c'], item['v']) for item in data.get('results', [])]

    return data
  
  async def fetch_all_stock(self):
    print(f"Fetching all stock data from {self.all_stock}")
    url = f"{self.all_stock}tickers"
    params = {
        "market": "stocks",
        "active": "true",
        "sort": "ticker",
        "order": "asc",
        "limit": 1000,
        "apiKey": self.api_key
    }
    response = await self.session.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Error fetching data: {response.text}")
    data = response.json()


    return data


