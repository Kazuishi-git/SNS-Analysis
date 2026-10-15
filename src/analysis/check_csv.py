import csv
from pathlib import Path
from collections import Counter

csv_path = Path("data/raw/starbucks_limit_test.csv")

with csv_path.open("r", encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))

tweet_ids = [row["tweet_id"] for row in rows]
counts = Counter(tweet_ids)
duplicates = {
    tweet_id: count
    for tweet_id, count in counts.items()
    if count > 1
}


print("CSVレコード数:", len(rows))
print("ユニークな投稿数:", len(set(tweet_ids)))
print("重複投稿数:", sum(count - 1 for count in counts.values()))
print("重複した投稿IDの例:", list(duplicates.items())[:10])