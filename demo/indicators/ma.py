import pandas as pd

# 示例数据
data = {
    "price": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19,20,30]
}
df = pd.DataFrame(data)

# 计算 3 日移动平均
df["MA_3"] = df["price"].rolling(window=3).mean()

# 计算 5 日移动平均
df["MA_5"] = df["price"].rolling(window=5).mean()

print(df)
