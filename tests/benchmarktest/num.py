from decimal import Decimal
import time
import numpy as np

# 测试规模
N = 10_000_000

# ===============================
# Python 原生 int 列表运算
# ===============================
py_list = [i  for i in range(N)]
start = time.time()
py_sum = 0.0
for x in py_list:
    py_sum += x * 1 - 1  # 简单算术操作
end = time.time()
print(f"Python int list 运算耗时: {end - start:.4f} 秒")
print(f"Python int sum: {py_sum}")

# ===============================
# Python 原生 float 列表运算
# ===============================
py_list = [float(i) + 0.123 for i in range(N)]
start = time.time()
py_sum = 0.0
for x in py_list:
    py_sum += x * 1.01 - 0.01  # 简单算术操作
end = time.time()
print(f"Python float list 运算耗时: {end - start:.4f} 秒")
print(f"Python float sum: {py_sum:.2f}")

# ===============================
# Python Decimal list 运算
# ===============================
decimal_list = [Decimal(i) + Decimal('0.123') for i in range(N)]
start = time.time()
decimal_sum = Decimal(0)
for x in decimal_list:
    decimal_sum += x * Decimal('1.01') - Decimal('0.01')
end = time.time()
print(f"Decimal list 运算耗时: {end - start:.4f} 秒")
print(f"Decimal sum: {decimal_sum:.2f}")

# ===============================
# NumPy float64 向量化运算
# ===============================
np_arr = np.arange(N, dtype=np.float64) + 0.123
start = time.time()
np_res = np_arr * 1.01 - 0.01  # 向量化操作
np_sum = np_res.sum()
end = time.time()
print(f"NumPy float64 向量化运算耗时: {end - start:.4f} 秒")
print(f"NumPy float sum: {np_sum:.2f}")
