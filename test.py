from datetime import datetime, UTC

from src.collect.models import Event
from src.collect.x_posts import XPostCollector

event = Event(
    event_id = "starbucks_test",
    query = "スタバ 新作",
    start_time = datetime(2026, 7, 1, tzinfo=UTC),
    end_time = datetime(2026, 7, 2, tzinfo=UTC),
    max_tweet = 100,
)

collector = XPostCollector()
collector.collect(event)