import argparse
import asyncio
import os
from sqlalchemy import Integer, Double, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime, timedelta
from typing import cast, Optional
from tickbutcher.data.put_to_db import Exchange, TimeframeType


DATA_SOURCE_URL = os.environ.get("DATA_SOURCE_URL", "sqlite+aiosqlite:///./tmp/app.db")

async_engine = create_async_engine(DATA_SOURCE_URL)



parser = argparse.ArgumentParser(description="K 线数据录入")
parser.add_argument('--code', type=str, help='交易代码' , required=True)
parser.add_argument('--timeframe', type=str, help='时间框架' , required=True)
parser.add_argument('--start_date', type=str, help='开始时间' , required=True)
parser.add_argument('--end_date', type=str, help='结束时间' , required=True)
parser.add_argument('--exchange', type=str, help='交易所名称' , default='binance')
parser.add_argument('--limit', type=int, help='单次获取数量' , default=10)
parser.add_argument('--overwrite', type=bool, help='是否覆盖已存在数据', default=False)
parser.add_argument('--api_key', type=str, help='api请求认证', required=False)


# 解析命令行参数
args = parser.parse_args()

# args.code         "BTC/USDT" #"SOL/USDT"
# args.timeframe    '1h' #'15m' # 分钟m h小时 d天 M月
# args.start_date   '2020-01-01T00:00:00Z'
# args.end_date     '2024-12-01T00:00:00Z'
# exchange_name     'binance' # 'okx' #'binance'
# # type: ignore    #binance limit max 1000
# type: ignore      #False

code = cast(str, args.code)
timeframe:str = cast(str, args.timeframe)
start_date:str = cast(str, args.start_date)
end_date:str = cast(str, args.end_date) 
exchange_name:str = cast(str, args.exchange) 
limit:int = cast(int, args.limit)
overwrite:bool = args.overwrite
api_key:Optional[str] = cast(Optional[str], args.api_key)



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
async def record_data(symbol:str, 
                      exchange:Exchange, 
                      start_date:datetime, 
                      end_date:datetime,
                      timeframe:TimeframeType,
                      limit:int)->None:
    # 将时间转换为时间戳

  async_session = async_sessionmaker(async_engine, expire_on_commit=False)
  
  async with async_session() as session:
    if not overwrite:
      sql = select(DataEntity).order_by(DataEntity.timestamp.desc()).limit(1)

      data = await session.scalar(sql)
      if data is not None:
          since_timestamp = data.timestamp
          start_date = datetime.fromtimestamp(since_timestamp, tz=start_date.tzinfo)

    while True:

      data = await exchange.fetch_ohlcv(symbol, timeframe, start_time=start_date, limit=limit)

      if len(data) == 0:
        break  # 如果没有数据返回，退出循环
      
      for item in data:
        if item[0] > int(end_date.timestamp() * 1000):
            break
        
        entity = DataEntity(timestamp=item[0], open=item[1], high=item[2],  low=item[3], close=item[4], volume=item[5])
        session.add(entity)
      
      start_date = datetime.fromtimestamp(data[-1][0] / 1000, tz=start_date.tzinfo) + timedelta(milliseconds=1)
      if start_date >= end_date:
        break
      print(f"Fetched {len(data)} records, next since: {start_date}")
      await session.flush()
      await session.commit()
      
    await session.flush()
    await session.commit()

async def main():
  global start_date, end_date, limit
  async with async_engine.begin() as conn:
        # 创建表
        await conn.run_sync(DataEntity.metadata.create_all)

  if exchange_name == 'binance':
      from . import Binance
      exchange = Binance()
  elif exchange_name == 'polygon':
      from . import PolygonEx
      exchange = PolygonEx(all_stock = "https://api.polygon.io/v3/reference/", candle_url = "https://api.polygon.io/v2/",api_key = api_key)
    
  else:
    raise Exception(f"不支持的交易所: {exchange_name}")

  

  if start_date.endswith("Z"): 
      start_date = start_date.replace("Z", "+00:00")
  if end_date.endswith("Z"):
      end_date = end_date.replace("Z", "+00:00")

  await record_data(code, 
                    exchange, 
                    timeframe=TimeframeType[timeframe], 
                    start_date=datetime.fromisoformat(start_date), 
                    end_date=datetime.fromisoformat(end_date),
                    limit=limit
                    )



if __name__ == "__main__":
  asyncio.run(main())
  
