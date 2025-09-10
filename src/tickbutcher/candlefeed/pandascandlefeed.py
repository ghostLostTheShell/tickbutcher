from datetime import datetime
from typing import List, Optional
from zoneinfo import ZoneInfo
from tickbutcher.brokers.trading_pair import TradingPair
from tickbutcher.candlefeed import TimeframeType
from pandas import DataFrame
import pandas as pd
from tickbutcher.candlefeed.candlefeed import CandleFeed

class PandasCandleFeed(CandleFeed):
  """基于Pandas的K线数据源
  
  Note: 如果下列dataframe部分为空，可能导致自下向上查找更小时间间隔K线时失败"""
  timeframe_s1:Optional[DataFrame] = None
  timeframe_min1:Optional[DataFrame] = None
  timeframe_min5:Optional[DataFrame] = None
  timeframe_min15:Optional[DataFrame] = None
  timeframe_h1:Optional[DataFrame] = None
  timeframe_h4:Optional[DataFrame] = None
  timeframe_d1:Optional[DataFrame] = None
  timeframe_w1:Optional[DataFrame] = None
  timeframe_mo1:Optional[DataFrame] = None
  timeframe_y1:Optional[DataFrame] = None

  
  def __init__(self, *, 
               trading_pair:TradingPair,
               timeframe_level:TimeframeType,
               dataframe:DataFrame,
               timezone:Optional[ZoneInfo]=None):

    super().__init__(trading_pair=trading_pair, timeframe_level=timeframe_level, timezone=timezone)
    
    if timeframe_level is  TimeframeType.sec1:
      ## 检查index的步进是否为1秒
      first100_idx = dataframe.index[:100]
      if not (pd.Series(first100_idx).diff().dropna() == 1000).all():
        raise ValueError("Dataframe index is not 1 second apart")
    else:
      raise NotImplementedError(f"{timeframe_level} timeframe validation not implemented yet")

    self.load_data(dataframe, timeframe_level)

  def load_data(self, data:DataFrame, timeframe:TimeframeType):
    if timeframe == TimeframeType.sec1:
      self.timeframe_s1 = data
    elif timeframe == TimeframeType.min1:
      self.timeframe_min1 = data
    elif timeframe == TimeframeType.min5:
      self.timeframe_min5 = data
    elif timeframe == TimeframeType.min15:
      self.timeframe_min15 = data
    elif timeframe == TimeframeType.h1:
      self.timeframe_h1 = data
    elif timeframe == TimeframeType.h4:
      self.timeframe_h4 = data
    elif timeframe == TimeframeType.d1:
      self.timeframe_d1 = data
    elif timeframe == TimeframeType.w1:
      self.timeframe_w1 = data
    elif timeframe == TimeframeType.mo1:
      self.timeframe_mo1 = data
    elif timeframe == TimeframeType.y1:
      self.timeframe_y1 = data
    else:
      raise ValueError(f"Unsupported timeframe: {timeframe}")

  def get_position_index_list(self) -> List[int]:
    dataframe = None
    if self.timeframe_level == TimeframeType.sec1:
      dataframe = self.timeframe_s1
    elif self.timeframe_level == TimeframeType.min1:
      dataframe = self.timeframe_min1
    elif self.timeframe_level == TimeframeType.min5:
      dataframe = self.timeframe_min5
    elif self.timeframe_level == TimeframeType.min15:
      dataframe = self.timeframe_min15
    elif self.timeframe_level == TimeframeType.h1:
      dataframe = self.timeframe_h1
    elif self.timeframe_level == TimeframeType.h4:
      dataframe = self.timeframe_h4
    elif self.timeframe_level == TimeframeType.d1:
      dataframe = self.timeframe_d1
    elif self.timeframe_level == TimeframeType.w1:
      dataframe = self.timeframe_w1
    elif self.timeframe_level == TimeframeType.mo1:
      dataframe = self.timeframe_mo1
    elif self.timeframe_level == TimeframeType.y1:
      dataframe = self.timeframe_y1
    else:
      raise ValueError("No valid timeframe data available")

    if dataframe is None:
      raise ValueError("No valid timeframe data available")

    return dataframe.index # type: ignore

  def get_ohlcv(self, position:int, *, timeframe:TimeframeType, offset:int=0, length:int=1)->Series[Any] | DataFrame:# type: ignore
    match timeframe:
      case TimeframeType.sec1:
        return self.sec1(position, offset=offset, length=length)
      case TimeframeType.min1:
        return self.min1(position, offset=offset, length=length)
      case TimeframeType.min5:
        return self.min1(position, offset=offset, length=length)
      case TimeframeType.min15:
        return self.sec1(position, offset=offset, length=length)
      case TimeframeType.h1:
        return self.sec1(position, offset=offset, length=length)
      case TimeframeType.h4:
        return self.sec1(position, offset=offset, length=length)
      case TimeframeType.d1:
        return self.sec1(position, offset=offset, length=length)
      case TimeframeType.w1:
        return self.sec1(position, offset=offset, length=length)
      case TimeframeType.mo1:
        return self.sec1(position, offset=offset, length=length)
      case TimeframeType.y1:
        return self.sec1(position, offset=offset, length=length)
      case _:
        pass

  def sec1(self, position:int, *, offset:int=0, length:int=1):
    if self.timeframe_s1 is None:
      raise ValueError("No sec1 timeframe data available")
    if self.timeframe_level.value > TimeframeType.sec1.value:
      raise ValueError(f"Current timeframe level {self.timeframe_level} is higher than sec1")
    
    if offset == 0:
      if length == 1:
        return self.timeframe_s1.loc[position]
      else:
        start = position + (offset*1000*length)
        return self.timeframe_s1.loc[start:position]
          
    else:
      if length == 1:
        return self.timeframe_s1.loc[position + (offset*1000)]
      else:
        position = position + (offset*1000)
        start = position + (offset*1000*length)
        return self.timeframe_s1.loc[start:position]
        
  def min1(self, position:int, *, offset:Optional[int]=0, length:int=1):
    """ 获取1分钟时间框架的k线

    Args:
        position (_type_): 获取的位置

    Raises:
        ValueError: _description_
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    if self.timeframe_min1 is None:
      raise ValueError("No min1 timeframe data available")

    if self.timeframe_level is TimeframeType.sec1:
      if offset == 0:
        sec = position % 60000
        if sec == 0:
          return self.sec1(position)
        else:
          start_index = position - sec
          sum_volume = self.timeframe_s1.loc[start_index:position, "volume"].sum()
          high = self.timeframe_s1.loc[start_index:position, "high"].max()
          low = self.timeframe_s1.loc[start_index:position, "low"].min()
          close = self.timeframe_s1.loc[position, "close"]
          open = self.timeframe_s1.loc[start_index, "open"]
          return pd.Series({
              "volume": sum_volume,
              "high": high,
              "low": low,
              "close": close,
              "open": open
          })
      else:
        position = position + self.timezone_offset + (offset * 1000 * 60)
        return self.timeframe_min1.loc[position]

    return self.timeframe_min1.loc[position]

  def min5(self, position, offset:Optional[int]=0, length:int=1):
    """ 获取5分钟时间框架的k线

    Args:
        position (_type_): 获取的位置

    Raises:
        ValueError: _description_
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    if self.timeframe_min5 is None:
      raise ValueError("No min5 timeframe data available")

    if self.timeframe_level.value >= TimeframeType.min5.value:
        if offset == 0:
            return self.timeframe_min5.loc[position]
        
        position = position + self.timezone_offset + (offset * 1000 * 60 * 5)
        return self.timeframe_min5.loc[position]

    else:
      if offset == 0:
        min = position % (1000 * 60 * 5)
        if min == 0:
          return self.min1(position)
        else:
          start_index = position - min
          sum_volume = self.timeframe_min1.loc[start_index:position, "volume"].sum()
          high = self.timeframe_min1.loc[start_index:position, "high"].max()
          low = self.timeframe_min1.loc[start_index:position, "low"].min()
          close = self.timeframe_min1.loc[position, "close"]
          open = self.timeframe_min1.loc[start_index, "open"]
          return pd.Series({
              "volume": sum_volume,
              "high": high,
              "low": low,
              "close": close,
              "open": open
          })
      else:
        position = position + self.timezone_offset + (offset * 1000 * 60 * 5)
        return self.timeframe_min5.loc[position]

  def min15(self, position, offset:Optional[int]=0, length:int=1):
      """ 获取15分钟时间框架的k线

      Args:
          position (_type_): 获取的位置

      Raises:
          ValueError: _description_
          ValueError: _description_

      Returns:
          _type_: _description_
      """
      if self.timeframe_min15 is None:
        raise ValueError("No min15 timeframe data available")

      if self.timeframe_level.value >= TimeframeType.min15.value:
          if offset == 0:
              return self.timeframe_min15.loc[position]

          position = position + self.timezone_offset + (offset * 1000 * 60 * 15)
          return self.timeframe_min15.loc[position]

      else :
        if offset == 0:
          min5 = position % (1000 * 60 * 15)
          if min5 == 0:
            return self.min5(position)
          else:
            start_index = position - min5
            sum_volume = self.timeframe_min5.loc[start_index:position, "volume"].sum()
            high = self.timeframe_min5.loc[start_index:position, "high"].max()
            low = self.timeframe_min5.loc[start_index:position, "low"].min()
            close = self.timeframe_min5.loc[position, "close"]
            open = self.timeframe_min5.loc[start_index, "open"]
            return pd.Series({
                "volume": sum_volume,
                "high": high,
                "low": low,
                "close": close,
                "open": open
            })
        else:
          position = position + self.timezone_offset + (offset * 1000 * 60 * 15)
          return self.timeframe_min15.loc[position]

  def h1(self, position, offset:Optional[int]=0, length:int=1):
      """ 获取1小时 时间框架的k线

      Args:
          position (_type_): 获取的位置

      Raises:
          ValueError: _description_
          ValueError: _description_

      Returns:
          _type_: _description_
      """
      if self.timeframe_h1 is None:
        raise ValueError("No h1 timeframe data available")

      if self.timeframe_level.value >= TimeframeType.h1.value:
          if offset == 0:
              return self.timeframe_h1.loc[position]

          position = position + self.timezone_offset + (offset * 1000 * 60 * 60)
          return self.timeframe_h1.loc[position]

      else :
        if offset == 0:
          min15 = position % (1000 * 60 * 60)
          if min15 == 0:
            return self.min15(position)
          else:
            start_index = position - min15
            sum_volume = self.timeframe_min15.loc[start_index:position, "volume"].sum()
            high = self.timeframe_min15.loc[start_index:position, "high"].max()
            low = self.timeframe_min15.loc[start_index:position, "low"].min()
            close = self.timeframe_min15.loc[position, "close"]
            open = self.timeframe_min15.loc[start_index, "open"]
            return pd.Series({
                "volume": sum_volume,
                "high": high,
                "low": low,
                "close": close,
                "open": open
            })
        else:
          position = position + self.timezone_offset + (offset * 1000 * 60 * 60)
          return self.timeframe_h1.loc[position]

  def h4(self, position, offset:Optional[int]=0, length:int=1):
      """ 获取4小时 时间框架的k线

      Args:
          position (_type_): 获取的位置

      Raises:
          ValueError: _description_
          ValueError: _description_

      Returns:
          _type_: _description_
      """
      if self.timeframe_h4 is None:
        raise ValueError("No h4 timeframe data available")

      if self.timeframe_level.value >= TimeframeType.h4.value:
          if offset == 0:
              return self.timeframe_h4.loc[position]

          position = position + self.timezone_offset + (offset * 1000 * 60 * 60 * 4)
          return self.timeframe_h4.loc[position]

      else :
        if offset == 0:
          h1 = position % (1000 * 60 * 60 * 4)
          if h1 == 0:
            return self.h1(position)
          else:
            start_index = position - h1
            sum_volume = self.timeframe_h1.loc[start_index:position, "volume"].sum()
            high = self.timeframe_h1.loc[start_index:position, "high"].max()
            low = self.timeframe_h1.loc[start_index:position, "low"].min()
            close = self.timeframe_h1.loc[position, "close"]
            open = self.timeframe_h1.loc[start_index, "open"]
            return pd.Series({
                "volume": sum_volume,
                "high": high,
                "low": low,
                "close": close,
                "open": open
            })
        else:
          position = position + self.timezone_offset + (offset * 1000 * 60 * 60 * 4)
          return self.timeframe_h4.loc[position]

  def d1(self, position, offset:Optional[int]=0, length:int=1):
      """ 获取1天时间框架的k线

      Args:
          position (_type_): 获取的位置

      Raises:
          ValueError: _description_
          ValueError: _description_

      Returns:
          _type_: _description_
      """
      if self.timeframe_d1 is None:
        raise ValueError("No d1 timeframe data available")

      if self.timeframe_level.value >= TimeframeType.d1.value:
          if offset == 0:
              return self.timeframe_d1.loc[position]

          position = position + self.timezone_offset + (offset * 1000 * 60 * 60 * 24)
          return self.timeframe_d1.loc[position]

      else :
        if offset == 0:
          h4 = position % (1000 * 60 * 60 * 24)
          if h4 == 0:
            return self.h4(position)
          else:
            start_index = position - h4
            sum_volume = self.timeframe_h4.loc[start_index:position, "volume"].sum()
            high = self.timeframe_h4.loc[start_index:position, "high"].max()
            low = self.timeframe_h4.loc[start_index:position, "low"].min()
            close = self.timeframe_h4.loc[position, "close"]
            open = self.timeframe_h4.loc[start_index, "open"]
            return pd.Series({
                "volume": sum_volume,
                "high": high,
                "low": low,
                "close": close,
                "open": open
            })
        else:
          position = position + self.timezone_offset + (offset * 1000 * 60 * 60 * 24)
          return self.timeframe_d1.loc[position]

  def w1(self, position, offset:Optional[int]=0,length:int=1):
      """ 获取1周时间框架的k线

      Args:
          position (_type_): 获取的位置

      Raises:
          ValueError: _description_
          ValueError: _description_

      Returns:
          _type_: _description_
      """
      if self.timeframe_w1 is None:
        raise ValueError("No w1 timeframe data available")

      if self.timeframe_level.value >= TimeframeType.w1.value:
          if offset == 0:
              return self.timeframe_w1.loc[position]

          position = position + self.timezone_offset + (offset * 1000 * 60 * 60 * 24 * 7)
          return self.timeframe_w1.loc[position]

      else :
        if offset == 0:
          d1 = position % (1000 * 60 * 60 * 24 * 7)
          if d1 == 0:
            return self.d1(position)
          else:
            start_index = position - d1
            sum_volume = self.timeframe_d1.loc[start_index:position, "volume"].sum()
            high = self.timeframe_d1.loc[start_index:position, "high"].max()
            low = self.timeframe_d1.loc[start_index:position, "low"].min()
            close = self.timeframe_d1.loc[position, "close"]
            open = self.timeframe_d1.loc[start_index, "open"]
            return pd.Series({
                "volume": sum_volume,
                "high": high,
                "low": low,
                "close": close,
                "open": open
            })
        else:
          position = position + self.timezone_offset + (offset * 1000 * 60 * 60 * 24 * 7)
          return self.timeframe_w1.loc[position]


  def mo1(self, position, offset:Optional[int]=0, length:int=1):
      """ 获取1周时间框架的k线

      Args:
          position (_type_): 获取的位置

      Raises:
          ValueError: _description_
          ValueError: _description_

      Returns:
          _type_: _description_
      """
      if self.timeframe_mo1 is None:
        raise ValueError("No mo1 timeframe data available")

      if self.timeframe_level.value >= TimeframeType.mo1.value:
          if offset == 0:
              return self.timeframe_mo1.loc[position]

          position = position + self.timezone_offset + (offset * 1000 * 60 * 60 * 24 * 30)
          return self.timeframe_mo1.loc[position]

      else :
        if offset == 0:
          w1 = position % (1000 * 60 * 60 * 24 * 30)
          if w1 == 0:
            return self.w1(position)
          else:
            start_index = position - w1
            sum_volume = self.timeframe_w1.loc[start_index:position, "volume"].sum()
            high = self.timeframe_w1.loc[start_index:position, "high"].max()
            low = self.timeframe_w1.loc[start_index:position, "low"].min()
            close = self.timeframe_w1.loc[position, "close"]
            open = self.timeframe_w1.loc[start_index, "open"]
            return pd.Series({
                "volume": sum_volume,
                "high": high,
                "low": low,
                "close": close,
                "open": open
            })
        else:
          position = position + self.timezone_offset + (offset * 1000 * 60 * 60 * 24 * 30)
          return self.timeframe_mo1.loc[position]

  def y1(self, position, offset:Optional[int]=0, length:int=1):
      """ 获取1年时间框架的k线

      Args:
          position (_type_): 获取的位置

      Raises:
          ValueError: _description_
          ValueError: _description_

      Returns:
          _type_: _description_
      """
      if self.timeframe_y1 is None:
        raise ValueError("No y1 timeframe data available")

      if self.timeframe_level.value >= TimeframeType.y1.value:
          if offset == 0:
              return self.timeframe_y1.loc[position]

          position = position + self.timezone_offset + (offset * 1000 * 60 * 60 * 24 * 365)
          return self.timeframe_y1.loc[position]

      else :
        if offset == 0:
          mo1 = position % (1000 * 60 * 60 * 24 * 365)
          if mo1 == 0:
            return self.mo1(position)
          else:
            start_index = position - mo1
            sum_volume = self.timeframe_mo1.loc[start_index:position, "volume"].sum()
            high = self.timeframe_mo1.loc[start_index:position, "high"].max()
            low = self.timeframe_mo1.loc[start_index:position, "low"].min()
            close = self.timeframe_mo1.loc[position, "close"]
            open = self.timeframe_mo1.loc[start_index, "open"]
            return pd.Series({
                "volume": sum_volume,
                "high": high,
                "low": low,
                "close": close,
                "open": open
            })
        else:
          position = position + self.timezone_offset + (offset * 1000 * 60 * 60 * 24 * 365)
          return self.timeframe_y1.loc[position]

def load_dataframe_from_sql(*, 
                            inst_id:str, 
                            timeframe:str, 
                            start_date:datetime, 
                            end_date:datetime, 
                            data_source_url:str):
  
  _start_date = start_date.timestamp() * 1000
  _end_date = end_date.timestamp() * 1000
  from sqlalchemy import create_engine  
  engine = create_engine(data_source_url)  
  
  with engine.connect() as conn, conn.begin():
    
    sql_statement = f'SELECT `timestamp`, `open`, `high`, `low`, `close`, \
      `volume` FROM `t_{inst_id}_{timeframe}` WHERE `timestamp` BETWEEN {_start_date} AND {_end_date}'
      
    df = pd.read_sql_query(sql_statement, conn, index_col='timestamp') # type: ignore


  # df.index = pd.to_datetime(df.index, unit='ms', utc=True).tz_convert('UTC')  # 转换时间戳
  
  return df