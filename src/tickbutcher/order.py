from tickbutcher.products import FinancialInstrument


class Order():
  def __init__(self, financial_type:FinancialInstrument, quantity:int, price:float):
    self.id = None  
    self.financial_type = financial_type
    self.quantity = quantity
    self.price = price
