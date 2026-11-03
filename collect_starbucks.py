from datetime import datetime
from zoneinfo import ZoneInfo

from src.collect.models import Event
from src.collect.x_posts import XPostCollector





QUERY = (
    '(スタバ OR スターバックス OR Starbucks) '
    '(フラペチーノ OR 新作) '
    'lang:ja -is:retweet'
)

JST = ZoneInfo("Asia/Tokyo")

event = Event(
    event_id="starbucks_new_20260907",
    query=QUERY,
    start_time=datetime(2026, 9, 7, 0, 0, tzinfo=JST),
    end_time=datetime(2026, 9, 8, 0, 0, tzinfo=JST),
    max_tweet=500,
)

collector = XPostCollector()
collector.collect(event)