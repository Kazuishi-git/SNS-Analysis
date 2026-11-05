# このファイルはデータだけを表現するためのもの

from dataclasses import dataclass
from datetime import datetime

@dataclass
class Event:
    event_id : str
    query : str
    start_time : datetime
    end_time : datetime
    max_tweet : int

@dataclass
class Tweet:
    event_id : str
    tweet_id : str
    author_id : str
    created_at : datetime
    retrieved_at : datetime
    text : str
    likes : int
    retweets : int
    replies : int
    quotes : int

@dataclass
class User:
    author_id : str
    followers_count : int
    following_count : int
    tweet_count : int
    listed_count : int
    retrieved_at : datetime # フォロワー数は変動するため、いつ取得した情報か記録
