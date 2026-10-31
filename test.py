from datetime import datetime, UTC

from src.collect.models import Event
from src.collect.x_posts import XPostCollector

event = Event(
    event_id="starbucks_20261026",
    query='("スタバ" OR Starbucks OR スターバックス) lang:ja -is:retweet',
    start_time=datetime(2026, 10, 25, tzinfo=UTC),
    end_time=datetime(2026, 10, 26, tzinfo=UTC),
    max_tweet=200,
)

collector = XPostCollector()
collector.collect(event)