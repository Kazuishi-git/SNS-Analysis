import csv
from datetime import UTC, datetime

from src.collect.models import Tweet
from src.collect.writer import CSVWriter


writer = CSVWriter()

# テスト用のCSVファイル名
filename = "writer_duplicate_test3.csv"

# テスト用の投稿データを作成する
now = datetime.now(UTC)

tweet1 = Tweet(
    event_id="writer_test",
    tweet_id="test_001",
    author_id="user_001",
    created_at=now,
    retrieved_at=now,
    text="テスト投稿1",
    likes=10,
    retweets=2,
    replies=1,
    quotes=0,
)

tweet2 = Tweet(
    event_id="writer_test",
    tweet_id="test_002",
    author_id="user_002",
    created_at=now,
    retrieved_at=now,
    text="テスト投稿2",
    likes=20,
    retweets=3,
    replies=2,
    quotes=1,
)

# 1回目：新しい投稿を保存する
writer.write(filename, [tweet1, tweet1, tweet2])

# 2回目：同じ投稿をもう一度保存しようとする
#writer.write(filename, [tweet1, tweet2])

# CSVを読み込んで結果を確認する
csv_path = writer.output_dir / filename

with csv_path.open("r", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

tweet_ids = [row["tweet_id"] for row in rows]

print("CSVレコード数:", len(rows))
print("投稿ID:", tweet_ids)
print("重複がないか:", len(tweet_ids) == len(set(tweet_ids)))