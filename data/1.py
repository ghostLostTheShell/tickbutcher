import ccxt
import pandas as pd
from datetime import datetime

# 初始化ccxt连接
exchange = ccxt.binance()

# 获取数据的函数
def fetch_binance_data(symbol, timeframe='1h', since='2022-01-01T00:00:00Z', limit=5000):
    # 将时间转换为时间戳
    since_timestamp = exchange.parse8601(since)
    ohlcv = []

    while True:
        # 获取K线数据
        data = exchange.fetch_ohlcv(symbol, timeframe, since=since_timestamp, limit=limit)
        if len(data) == 0:
            break  # 如果没有数据返回，退出循环
        
        ohlcv += data
        
        # 更新下一次请求的起始时间（获取到的最后一条数据的时间戳）
        since_timestamp = ohlcv[-1][0] + 1  # 1毫秒的偏移，防止获取到重复的数据

    # 将数据转换为Pandas DataFrame
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')  # 转换时间戳
    df.set_index('timestamp', inplace=True)

    return df

# 设置币种和时间框架
symbol = 'BTC/USDT'  # 交易对
since = '2021-01-01T00:00:00Z'  # 获取的数据起始时间

# 获取 15 分钟、1 小时和 4 小时的数据
timeframes = [ '5m']
dataframes = {}

for timeframe in timeframes:
    df = fetch_binance_data(symbol, timeframe, since)
    dataframes[timeframe] = df
    # 将数据保存为 CSV 文件
    csv_filename = f"{symbol.replace('/', '-')}_{timeframe}.csv"
    df.to_csv(csv_filename)
    print(f"{csv_filename} saved successfully!")

