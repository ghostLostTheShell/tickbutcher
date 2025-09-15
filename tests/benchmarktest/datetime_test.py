# type: ignore
import timeit
import datetime

# 方法A：datetime.fromtimestamp
def method_datetime(ts):
    dt = datetime.datetime.fromtimestamp(ts)
    is_hour = (dt.minute == 0 and dt.second == 0)
    is_minute = (dt.second == 0)
    is_second = (dt.microsecond == 0)
    return is_hour, is_minute, is_second

# 方法B：整数取模
def method_modulo(ts): 
    t = int(ts)
    is_second = (ts == t)
    is_minute = (t % 60 == 0)
    is_hour = (t % 3600 == 0)
    return is_hour, is_minute, is_second

# 测试参数
ts = 1694505600.0  # 一个固定的时间戳

# 性能测试
n = 60 * 60 * 24 * 365  # 模拟一个月的每秒调用
time_dt = timeit.timeit(lambda: method_datetime(ts), number=n)
time_mod = timeit.timeit(lambda: method_modulo(ts), number=n)

print(f"datetime.fromtimestamp 方法: {time_dt:.6f} 秒 / {n} 次")
print(f"取模运算 方法: {time_mod:.6f} 秒 / {n} 次")
print(f"性能提升倍数: {time_dt/time_mod:.1f}x")
