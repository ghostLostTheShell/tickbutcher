from datetime import datetime
from tickbutcher.candlefeed.pandascandlefeed import load_dataframe_from_sql
from . import sol
from . import btc

def get_sol_usdt_1s_and_1min():
    test_start_date = datetime.fromisoformat("2025-01-02T00:00:00+00:00:00")
    end_start_date = datetime.fromisoformat("2025-01-10T00:00:00+00:00:00")

    sol_usdt_1s_dataframe = load_dataframe_from_sql(inst_id='SOL/USDT', 
                                          timeframe='1s', 
                                          start_date=test_start_date, 
                                          end_date=end_start_date, 
                                          data_source_url="sqlite:///./tmp/app.db")
    sol_usdt_1m = load_dataframe_from_sql(inst_id='SOL/USDT', 
                                          timeframe='1m', 
                                          start_date=test_start_date, 
                                          end_date=end_start_date, 
                                          data_source_url="sqlite:///./tmp/app.db")
    
    return (sol_usdt_1s_dataframe, sol_usdt_1m)