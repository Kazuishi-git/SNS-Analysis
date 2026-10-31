from datetime import datetime
from zoneinfo import ZoneInfo

from src.collect.models import Event
from src.collect.x_posts import XPostCollector

COMMON_QUERY = (
    '(スタバ OR Starbucks OR スターバックス) '
    'フラペチーノ lang:ja -is:retweet'
)

UNIQUE_QUERY = (
    ' ("ぎゅぎゅっとオレンジ" OR '
    ' "オレンジ＆マンゴー" OR '
    ' "オレンジマンゴー" OR '
    ' "オレンジ" OR '
    ' "マンゴー" OR '
    ' "オレンジマンゴー") '
)



query = f"{COMMON_QUERY} {UNIQUE_QUERY}"

JST = ZoneInfo("Asia/Tokyo")

event = Event(
    event_id="starbucks_new_20260717",
    query=query,
    start_time=datetime(2026, 7, 17, 0, 0, tzinfo=JST),
    end_time=datetime(2026, 7, 18, 0, 0, tzinfo=JST),
    max_tweet=500,
)

collector = XPostCollector()
collector.collect(event)