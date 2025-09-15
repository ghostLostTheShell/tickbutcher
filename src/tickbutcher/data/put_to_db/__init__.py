
import httpx
from typing import Any, Dict, List, Optional


class Binance:
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
    
  
  async def fetch_ohlcv(self, symbol:str, timeframe:str, start_time:int, end_time:int, limit:int=500):
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
        "endTime": end_time,
        "limit": limit
    }
    response = await self.session.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Error fetching data: {response.text}")
    data = response.json()
    return data