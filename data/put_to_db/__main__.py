 # type: ignore
import argparse
import asyncio
import os
import ccxt
from sqlalchemy import *
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import *
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.asyncio import async_sessionmaker



DATA_SOURCE_URL = os.environ.get("DATA_SOURCE_URL") 
if DATA_SOURCE_URL is None:
  DATA_SOURCE_URL = "sqlite+aiosqlite:///./app.db"


async_engine = create_async_engine(DATA_SOURCE_URL)



parser = argparse.ArgumentParser(description="K 线数据录入")
parser.add_argument('--code', type=str, help='交易代码' , required=True)
parser.add_argument('--timeframe', type=str, help='时间框架' , required=True)
parser.add_argument('--start_date', type=str, help='开始时间' , required=True)
parser.add_argument('--end_date', type=str, help='结束时间' , required=True)
parser.add_argument('--exchange', type=str, help='交易所名称' , default='binance')
parser.add_argument('--limit', type=int, help='单次获取数量' , default=1000)
parser.add_argument('--overwrite', type=bool, help='是否覆盖已存在数据', default=False)

# 解析命令行参数
args = parser.parse_args()

code = args.code #"BTC/USDT" #"SOL/USDT" #
timeframe = args.timeframe #'1h' #'15m' # 分钟m h小时 d天 M月
start_date =  args.start_date #'2020-01-01T00:00:00Z'
end_date = args.end_date #'2024-12-01T00:00:00Z'
exchange_name = args.exchange #'binance' # 'okx' #'binance'
limit = args.limit #binance limit max 1000
overwrite = args.overwrite #False

class BaseEntity(AsyncAttrs, DeclarativeBase):
    pass


class DataEntity(BaseEntity):
    __tablename__                   = f"t_{code}_{timeframe}"
    id: Mapped[int]                 = mapped_column(Integer(), primary_key=True, autoincrement=True)
    timestamp:Mapped[int]           = mapped_column(Integer(), unique=True)
    open:Mapped[float]              = mapped_column(Double())
    high:Mapped[float]              = mapped_column(Double())
    low:Mapped[float]               = mapped_column(Double())
    close:Mapped[float]             = mapped_column(Double())
    volume:Mapped[float]            = mapped_column(Double())

# 获取数据的函数
async def record_data(symbol, exchange, timeframe='1h', start_date='2022-01-01T00:00:00Z', end_date='2023-01-01T00:00:00Z'):
    # 将时间转换为时间戳
    since_timestamp = exchange.parse8601(start_date)
    end_timestamp = exchange.parse8601(end_date)
    
    async_session = async_sessionmaker(async_engine, expire_on_commit=False)
    
    async with async_session() as session:
      if not overwrite:
        sql = select(DataEntity).order_by(DataEntity.timestamp.desc()).limit(1)

        data = await session.scalar(sql)
        if data is not None:
            since_timestamp = data.timestamp

        ### 根据timeframe调整加上偏移量 1s|1m|15m
        if timeframe == '1s':
            since_timestamp += 1000
        elif timeframe == '1m':
            since_timestamp += 60000
        elif timeframe == '15m':
            since_timestamp += 900000
        elif timeframe == '1h':
            since_timestamp += 3600000
        elif timeframe == '1d':
            since_timestamp += 86400000

      while True:
        # 获取K线数据

        # 多线程获取数据，存在问题
        #   data = []
        #   thread_pool = []
        #   execution_count = 0
        #   start_time = time.time()

        #   while time.time() - start_time < 60 and execution_count < 3000:
        #       thread = Thread(target=lambda: data.append(exchange.fetch_ohlcv(symbol, timeframe, since=since_timestamp, limit=limit)))
        #       thread.start()
        #       thread_pool.append(thread)

        #   for thread in thread_pool:
        #       thread.join()

        data = exchange.fetch_ohlcv(symbol, timeframe, since=since_timestamp, limit=limit)

        if len(data) == 0:
            break  # 如果没有数据返回，退出循环
        
        for item in data:
        
        # select(exists().where(DataEntity.timestamp==item[0]))

            entity = DataEntity(timestamp=item[0], open=item[1], high=item[2],  low=item[3], close=item[4], volume=item[5])
            session.add(entity)

        
        since_timestamp = data[-1][0] + 1  # 1毫秒的偏移，防止获取到重复的数据
        if since_timestamp > end_timestamp:
            break
        
        print(f"Fetched {len(data)} records, next since: {since_timestamp}")
        await session.flush()
        await session.commit()
        
      await session.flush()
      await session.commit()

async def main():
  
  async with async_engine.begin() as conn:
        # 创建表
        await conn.run_sync(DataEntity.metadata.create_all)
  
  # 初始化ccxt连接
  exchange = getattr(ccxt, exchange_name)()
  await record_data(code, exchange, timeframe=timeframe, start_date=start_date, end_date=end_date)


if __name__ == "__main__":
  
  asyncio.run(main())
  
