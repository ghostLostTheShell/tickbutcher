import random

# ===============================================================
# 步骤 1: 基础类 (KData 和 indicator)
# ===============================================================

class KData:
    """K线数据结构"""
    def __init__(self, close=0):
        # 交叉判断只需要 close 价格
        self.close = close
    def __repr__(self):
        return f"C:{self.close:.2f}"

class indicator:
    """指标计算类"""
    def __init__(self, Kline, index, period):
        if len(Kline) <= index:
             raise IndexError("计算索引 (index) 超出 Kline 数据范围。")
        self.Kline = Kline
        self.index = index
        self.period = period
    
    def MA(self):   
        """计算简单移动平均线"""
        if self.index < self.period - 1:
            return None
        start_index = self.index - self.period + 1
        data_slice = self.Kline[start_index : self.index + 1]
        close_values = [d.close for d in data_slice]
        return sum(close_values) / len(close_values)

# ===============================================================
# 步骤 2: 蒙特卡洛数据生成器 (无需修改)
# ===============================================================

def generate_monte_carlo_kline(num_bars, initial_price=100.0, volatility=0.015):
    """生成模拟的 K-line 数据列表"""
    kline_data = []
    current_price = initial_price
    for _ in range(num_bars):
        change_percent = random.normalvariate(0, volatility)
        close_price = current_price * (1 + change_percent)
        kline_data.append(KData(close=max(1, close_price))) # 确保价格不为负
        current_price = close_price
    return kline_data

# ===============================================================
# 步骤 3: 主测试函数 (集成均线交叉逻辑)
# ===============================================================

def main():
    """
    运行蒙特卡洛模拟，测试均线交叉逻辑。
    """
    num_simulations = 5  # 运行5轮不同的模拟
    bars_per_simulation = 100 # 每轮模拟生成100根K线
    
    fast_period = 5
    slow_period = 10

    print(f"--- 开始蒙特卡洛模拟：均线交叉测试 (MA{fast_period} vs MA{slow_period}) ---")

    for i in range(num_simulations):
        print(f"\n{'='*20} 模拟轮次 {i + 1}/{num_simulations} {'='*20}")
        
        # 1. 生成一组全新的随机 Kline 数据
        Kline = generate_monte_carlo_kline(bars_per_simulation)
        
        # 初始化交叉计数器
        golden_cross_count = 0
        death_cross_count = 0

        # 2. 遍历生成的K线数据，寻找交叉点
        # 循环的起始点必须保证能计算前一天的慢线
        start_index = slow_period
        for idx in range(start_index, len(Kline)):
            try:
                # a. 计算当前点的快慢均线值
                current_ma_fast = indicator(Kline, index=idx, period=fast_period).MA()
                current_ma_slow = indicator(Kline, index=idx, period=slow_period).MA()

                # b. 计算前一点的快慢均线值
                previous_ma_fast = indicator(Kline, index=idx - 1, period=fast_period).MA()
                previous_ma_slow = indicator(Kline, index=idx - 1, period=slow_period).MA()
                
                cross_event = None

                # c. 进行交叉逻辑判断 (确保所有值都有效)
                if all([current_ma_fast, current_ma_slow, previous_ma_fast, previous_ma_slow]):
                    # 判断上穿（金叉）
                    if previous_ma_fast < previous_ma_slow and current_ma_fast > current_ma_slow:
                        cross_event = f"🟢 上穿 (金叉) at index {idx}"
                        golden_cross_count += 1

                    # 判断下穿（死叉）
                    elif previous_ma_fast > previous_ma_slow and current_ma_fast < current_ma_slow:
                        cross_event = f"🔴 下穿 (死叉) at index {idx}"
                        death_cross_count += 1
                
                # d. 如果发生了交叉事件，则打印详细信息
                if cross_event:
                    print(cross_event)
                    print(f"  - 前一状态 (idx={idx-1}): MA{fast_period}={previous_ma_fast:.2f}, MA{slow_period}={previous_ma_slow:.2f}")
                    print(f"  - 当前状态 (idx={idx}): MA{fast_period}={current_ma_fast:.2f}, MA{slow_period}={current_ma_slow:.2f}")

            except (ValueError, IndexError) as e:
                # 理论上，由于我们正确设置了 start_index，这里不应触发错误
                print(f"在索引 {idx} 处发生计算错误: {e}")
        
        # 3. 打印本轮模拟的总结
        print("-" * 50)
        if golden_cross_count == 0 and death_cross_count == 0:
            print("本轮模拟未发现任何均线交叉事件。")
        else:
            print(f"本轮模拟总结: 共发现 {golden_cross_count} 次金叉, {death_cross_count} 次死叉。")
        print("-" * 50)

    print("\n--- 蒙特卡洛模拟结束 ---")


# ===============================================================
# 运行主函数
# ===============================================================
if __name__ == "__main__":
    main()