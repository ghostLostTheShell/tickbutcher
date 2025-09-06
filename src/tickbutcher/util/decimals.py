"""工具函数：处理小数点位数的函数
"""

from decimal import Decimal


def get_decimal_places(value: float) -> int:
  """获取一个浮点数的小数位数"""
  d = Decimal(str(value))
  places:int = -d.as_tuple().exponent if d.as_tuple().exponent < 0 else 0 # type: ignore
  return places # type: ignore