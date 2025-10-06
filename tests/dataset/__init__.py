from datetime import datetime
from tickbutcher.candlefeed.pandascandlefeed import load_dataframe_from_sql
from . import sol
from . import btc
from pandas import DataFrame
from typing import Tuple, Optional

sol_usdt_1s_dataframe:Optional[DataFrame]=None
sol_usdt_1m_dataframe:Optional[DataFrame]=None
def get_sol_usdt_1s_and_1min() -> Tuple[DataFrame, DataFrame]:
  global sol_usdt_1s_dataframe, sol_usdt_1m_dataframe
  
  test_start_date = datetime.fromisoformat("2025-01-02T00:00:00+00:00:00")
  end_start_date = datetime.fromisoformat("2025-01-20T00:00:00+00:00:00")

  if sol_usdt_1s_dataframe is None:
      sol_usdt_1s_dataframe = load_dataframe_from_sql(inst_id='SOL/USDT',
                                                      timeframe='1s',
                                                      start_date=test_start_date,
                                                      end_date=end_start_date,
                                                      data_source_url="sqlite:///./tmp/app.db")
  if sol_usdt_1m_dataframe is None:
    sol_usdt_1m_dataframe = load_dataframe_from_sql(inst_id='SOL/USDT', 
                                          timeframe='1m', 
                                          start_date=test_start_date, 
                                          end_date=end_start_date, 
                                          data_source_url="sqlite:///./tmp/app.db")
  
  return (sol_usdt_1s_dataframe, sol_usdt_1m_dataframe)

__all__ = ['sol', 'btc', 'get_sol_usdt_1s_and_1min']