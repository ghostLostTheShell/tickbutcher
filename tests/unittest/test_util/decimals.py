from time import time
import unittest


def get_decimal_places(value: float, max_try:int=1000) -> int:
  """获取一个浮点数的小数位数"""
  i = 0
  while True:
    value = value * 10
    print(value)
    i += 1
    if value.is_integer():
      break

    if i > max_try:
      raise ValueError("Value has too many decimal places")
  return i

class TestGetDecimalPlaces(unittest.TestCase):

  def test_integer(self):
    start = time()
    v = 0.000000000000001
    #error 如果 v 太小 结果不正确
    i = get_decimal_places(v, max_try=1000000000000000)
    end = time()
    print(f"test_integer took {(end - start)* 1000} ms i is {i} v is {v * (10 ** i)} ")

    from decimal import Decimal
    start = time()
    d = Decimal(str(v))
    places = -d.as_tuple().exponent if d.as_tuple().exponent < 0 else 0 # type: ignore
    end = time()
    print(f"Decimal took {(end - start) * 1000} ms places is {places} v is {v * (10 ** places)} ")

  def test_float(self):

    pass