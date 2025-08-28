from tickbutcher.products import FinancialInstrument


class TradingPair():
  """
    String     base  
    String     quote  计价货币
  """
  base:FinancialInstrument #基础货币
  quote:FinancialInstrument #计价货币
  symbol:str      # 交易对符号，如 BTC/USDT
  id:str          # 交易对ID

  def __init__(self, *, 
               base: FinancialInstrument, 
               quote: FinancialInstrument,
               symbol: str,
               id: str) -> object:
      self.base = base
      self.quote = quote
      self.symbol = symbol
      self.id = id
      
