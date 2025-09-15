from datetime import datetime, timezone
from tickbutcher.data.put_to_db import Binance
from tickbutcher.log import ch_handler
binance = Binance()

import logging
logger = logging.getLogger("root")
logger.addHandler(ch_handler)
logger.setLevel(logging.DEBUG)   


async def main():
  
  start_time = int(datetime(2025, 1, 1, tzinfo=timezone.utc).timestamp()) * 1000
  end_time = int(datetime(2025, 1, 3, tzinfo=timezone.utc).timestamp()) * 1000
  p = await binance.exchange_info(symbol="BTC/USDC@P")
  print(f"exchange_info: \n{p}")
  
  print(start_time, end_time)
  a = await binance.fetch_ohlcv("BTC/USDC@P", "1h", start_time=start_time, end_time=end_time)

  print(a)
  
if __name__ == "__main__":
  import asyncio
  asyncio.run(main())
  