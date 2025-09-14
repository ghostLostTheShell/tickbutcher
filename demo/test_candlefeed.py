from datetime import datetime, timedelta, timezone as TimeZone
from tickbutcher.candlefeed import TimeframeType
from tickbutcher.candlefeed.pandascandlefeed import round_time


def test_round_time():
  ch = TimeZone(timedelta(hours=8))
  ch_offset = int(ch.utcoffset(None).total_seconds())
  ist = TimeZone(timedelta(hours=5, minutes=30))
  ist_offset = int(ist.utcoffset(None).total_seconds())
  
  start = 1735689720
  end = 1735789720 + (60 * 60 * 24 * 30)
  while True:

    if start > end:
      break
    #印度时间
    remainder = round_time(start, TimeframeType.d1, ist_offset)
    print("印度时间", datetime.fromtimestamp(start, tz=ist), "remainder:", timedelta(seconds=remainder))
    #中国时间
    remainder = round_time(start, TimeframeType.d1, ch_offset)
    print("中国时间", datetime.fromtimestamp(start, tz=ch), "remainder:", timedelta(seconds=remainder))
    remainder = round_time(start, TimeframeType.d1)
    print("UTC时间", datetime.fromtimestamp(start, tz=TimeZone.utc), "remainder:", timedelta(seconds=remainder))
    print("----")
    start += 60

test_round_time()