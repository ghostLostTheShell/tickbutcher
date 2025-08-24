import enum


"""订单操作类型"""
class OrderOptionType(enum.Enum):
  MarketOrder = 1
  LimitOrder = 2
  StopOrder = 3
  StopLimitOrder = 4
  TrailingStopOrder = 5
  Iceberg_Order = 6
  FillOrKillOrder = 7
  ImmediateOrCancelOrder = 8
  PostOnlyOrder = 9
  OneCancelsTheOtherOrder = 10
  TWAPOrder = 11

"""订单状态类型 （包含准备 and 市商返回类型）"""
class OrderProcessStatusType(enum.Enum):
  Created = 0       ### 已创建 (Created)
  Submitted = 1   ### 已提交 (Submitted)
  Padding = 2  ### 等待订单撮合 (Padding)
  Accepted = 3 ### 已接受 (Accepted) 预先扣除保证金
  PartiallyFilled = 4   ### 部分成交 (Partially Filled)
  Filled = 5   ### 完全成交 (Filled)
  Cancelled = 6   ### 已取消 (Cancelled)
  Rejected = 7   ### 拒绝 (Rejected)
  Completed = 8   ### 已完成 (Completed) 订单全部完成
  Expired = 9  ### 已失效 (Expired)
  Margin = 10  ### 保证金不足 （Margin）

