from datetime import datetime, timezone
from typing import List, Optional
from tickbutcher.brokers.trading_pair import TradingPair
from tickbutcher.candlefeed import TimeframeType
from pandas import DataFrame, Series
import pandas as pd
from tickbutcher.candlefeed.candlefeed import CandleFeed

_TF_MAP = {
  TimeframeType.sec1: 1,
  TimeframeType.min1: 60,
  TimeframeType.min5: 5*60,
  TimeframeType.min15: 15*60,
  TimeframeType.h1: 3600,
  TimeframeType.h4: 4*3600,
  TimeframeType.d1: 24*3600,
  TimeframeType.w1: 7*24*3600,
  TimeframeType.mo1: 30*24*3600,
  TimeframeType.y1: 365*24*3600}

def round_time(ts: int, timeframe: TimeframeType, offset: int = 0) -> int:
    """
    判断时间戳是否在指定时间框架的整点上，支持偏移。
    
    :param ts: 时间戳（秒级）
    :param offset: 偏移秒数，正数表示往后偏移，负数表示往前偏移
    :return: 返回偏移的秒数
    """
    if timeframe is TimeframeType.sec1:
        return 0  # 秒级K线不需要调整
      
    ts += offset  # 加上偏移
    tf_seconds = _TF_MAP[timeframe]
    return ts % tf_seconds

class PandasCandleFeed(CandleFeed):
  """基于Pandas的K线数据源
  
  Note: 如果下列dataframe部分为空，可能导致自下向上查找更小时间间隔K线时失败"""
  timeframe_dict:dict[TimeframeType, DataFrame]
  _cached_current_series:dict[TimeframeType, Series]

  def __init__(self, *, 
               trading_pair:TradingPair,
               timeframe_level:TimeframeType,
               dataframe:DataFrame,
               timezone:Optional[timezone]=None
               ):

    super().__init__(trading_pair=trading_pair, timeframe_level=timeframe_level, timezone=timezone)
    
    # if timeframe_level is  TimeframeType.sec1:
    #   ## 检查index的步进是否为1秒
    #   first100_idx = dataframe.index[:100]
    #   if not (pd.Series(first100_idx).diff().dropna() == 1000).all():
    #     raise ValueError("Dataframe index is not 1 second apart")
    # else:
    #   raise NotImplementedError(f"{timeframe_level} timeframe validation not implemented yet")
    self._cached_current_series = {}
    self.timeframe_dict = {}
    self.load_data(dataframe, timeframe_level)


    
  def load_data(self, data:DataFrame, timeframe:TimeframeType):
    self.disable_timeframe.remove(timeframe)
    self.timeframe_dict[timeframe] = data
      
  def get_dataframe(self, timeframe:TimeframeType) -> Optional[DataFrame]:
    return self.timeframe_dict.get(timeframe)
  
  def get_position_index_list(self) -> List[int]:
    dataframe = self.get_dataframe(self.timeframe_level)
    if dataframe is not None:
      return dataframe.index # type: ignore
    return []

  def agg_ohlcv(self, timeframe:TimeframeType, start:int, end:int) -> Series:
    dataframe = self.get_dataframe(timeframe)
    
    if dataframe is None:
      raise ValueError(f"No dataframe for timeframe {timeframe}")

    sum_volume = dataframe.loc[start:end, "volume"].sum()
    high = dataframe.loc[start:end, "high"].max()
    low = dataframe.loc[start:end, "low"].min()
    close = dataframe.loc[end, "close"]
    open = dataframe.loc[start, "open"]
    return pd.Series({
        "volume": sum_volume,
        "high": high,
        "low": low,
        "close": close,
        "open": open
    })
  
  def _get_current_cached_series_or_create(self, timeframe:TimeframeType) -> Series:
    series = self._cached_current_series.get(timeframe)
    if series is None:
      series = Series({
                        "volume": 0.0,
                        "high": 0.0,
                        "low": 0.0,
                        "close": 0.0,
                        "open": 0.0})
      self._cached_current_series[timeframe] = series
    return series

  def get_ohlcv(self, position:int, *, timeframe:TimeframeType, offset:int=0)-> 'Series':# type: ignore
    dataframe = self.get_dataframe(timeframe)
    if dataframe is None:
      raise ValueError(f"No dataframe for timeframe {timeframe}")
    remainder = round_time(position, timeframe, self.timezone_offset)
    if offset != 0:
      position = position - remainder + self.timezone_offset + (_TF_MAP[timeframe] * offset)

    if remainder != 0:
      position = position - remainder + self.timezone_offset
      return self._cached_current_series.get(
        timeframe, Series({
                        "volume": 0.0,
                        "high": 0.0,
                        "low": 0.0,
                        "close": 0.0,
                        "open": 0.0}, 
                        dtype='float64',
                        name=position)
      )
    return dataframe.loc[position] # type: ignore
  
  def update(self, position:int):
    for tf, _df in self.timeframe_dict.items():
      
      if tf in self.disable_timeframe or tf is self.timeframe_level:
        continue
      
      remainder = round_time(position, tf, self.timezone_offset)
      
      if remainder != 0:
        # 非整点时间，更新缓存
        
        series = self.get_ohlcv(position, timeframe=self.timeframe_level, offset=0)
        current_series = self._cached_current_series.get(tf)
        if current_series is None:
          current_series = Series({
                        "volume": series.volume,
                        "high": series.high,
                        "low": series.low,
                        "close": series.close,
                        "open": series.open}, 
                        dtype='float64',
                        name=position - remainder)
          self._cached_current_series[tf] = current_series
        else:
          current_series.volume += series.volume
          current_series.high = max(current_series.high, series.high)
          current_series.low = min(current_series.low, series.low) if current_series.low > 0 else series.low
          current_series.close = series.close
          # current_series.open = current_series.open # 开盘价不变     

      else:
        # 整点时间设置为当前最少框架的K线
        min_series = self.get_ohlcv(position, timeframe=self.timeframe_level, offset=0)
        current_series = Series({
                        "volume": min_series.volume,
                        "high": min_series.high,
                        "low": min_series.low,
                        "close": min_series.close,
                        "open": min_series.open}, 
                        dtype='float64',
                        name=position - remainder)
        self._cached_current_series[tf] = current_series

def load_dataframe_from_sql(*, 
                            inst_id:str, 
                            timeframe:str, 
                            start_date:datetime, 
                            end_date:datetime, 
                            data_source_url:str):
  
  _start_date = start_date.timestamp()
  _end_date = end_date.timestamp()
  from sqlalchemy import create_engine  
  engine = create_engine(data_source_url)  
  
  with engine.connect() as conn, conn.begin():
    
    sql_statement = f'SELECT `timestamp`, `open`, `high`, `low`, `close`, \
      `volume` FROM `t_{inst_id}_{timeframe}` WHERE `timestamp` BETWEEN {_start_date} AND {_end_date}'
      
    df = pd.read_sql_query(sql_statement, conn, index_col='timestamp') # type: ignore


  # df.index = pd.to_datetime(df.index, unit='ms', utc=True).tz_convert('UTC')  # 转换时间戳
  
  return df