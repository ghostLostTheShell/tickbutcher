class Position:
    """
    用于跟踪单一金融工具的持仓信息.
    """
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.quantity = 0         # 持仓数量 (正为多头, 负为空头)
        self.total_cost = 0.0     # 总持仓成本 (始终为正)
        self.avg_price = 0.0      # 开仓均价

    def transact(self, price: float, quantity: int, fee: float = 0.0):
        """
        处理一笔交易并更新持仓状态.
        quantity: 正数表示买入, 负数表示卖出.
        """
        # 判断是开仓/加仓还是平仓/减仓
        # is_opening: 交易方向与现有持仓方向相同，或现有持仓为0
        is_opening = (self.quantity == 0) or (quantity > 0 and self.quantity > 0) or (quantity < 0 and self.quantity < 0)

        trade_cost = price * abs(quantity) + fee

        if is_opening:
            # 开仓或加仓逻辑
            self.total_cost += trade_cost
            self.quantity += quantity
            # 重新计算开仓均价
            self.avg_price = self.total_cost / abs(self.quantity)
        else:
            # 平仓或减仓逻辑
            # 注意：平仓不改变 avg_price
            # 在这里可以计算已实现盈亏 (Realized PnL)
            realized_pnl = (price - self.avg_price) * abs(quantity) * (1 if self.quantity > 0 else -1) - fee
            print(f"平仓 {abs(quantity)} 股/手, 实现盈亏: {realized_pnl:.2f}")

            self.quantity += quantity
            # 减去平仓部分的成本
            self.total_cost = self.avg_price * abs(self.quantity)

            # 如果全部平仓，重置状态
            if self.quantity == 0:
                self.total_cost = 0.0
                self.avg_price = 0.0
        
        self.print_status()

    def print_status(self):
        print(f"--- 持仓状态: {self.symbol} ---")
        print(f"  数量: {self.quantity}")
        print(f"  均价: {self.avg_price:.2f}")
        print(f"  总成本: {self.total_cost:.2f}")
        print("--------------------------\n")

# 使用示例
pos = Position("AAPL")

print("第一次买入:")
pos.transact(price=10.00, quantity=1000, fee=5.0)

print("第二次买入 (加仓):")
pos.transact(price=12.00, quantity=500, fee=2.5)

print("卖出部分 (平仓):")
pos.transact(price=15.00, quantity=-300, fee=1.5)