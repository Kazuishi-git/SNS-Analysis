import csv
import pytest

from datetime import UTC, datetime
from pathlib import Path

from src.collect.models import Tweet
from src.collect.writer import CSVWriter

def create_tweet(tweet_id: str) -> Tweet:
    """ Create a test tweet."""
    # テスト用の投稿データを作成する
    now = datetime.now(UTC)

    return Tweet(
        event_id="writer_test",
        tweet_id=tweet_id,
        author_id="user_001",
        created_at=now,
        retrieved_at=now,
        text="テスト投稿",
        likes=10,
        retweets=2,
        replies=1,
        quotes=0,
    )


def read_tweet_ids(csv_path):
    """ Read tweet IDs from a CSV file."""

    with csv_path.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    return [row["tweet_id"] for row in rows]


def test_write_removes_duplicate_in_same_batch(tmp_path):
    """ Test duplicate removal within the same batch."""

    writer = CSVWriter(output_dir=tmp_path)

    tweet1 = create_tweet("test_001")
    tweet2 = create_tweet("test_002")

    writer.write(
        "test.csv",
        [tweet1, tweet1, tweet2]
    )

    tweet_ids = read_tweet_ids(tmp_path / "test.csv")

    assert len(tweet_ids) == 2
    assert set(tweet_ids) == {"test_001", "test_002"}

def test_write_removes_duplicates_across_multiple_calls(tmp_path):
    writer = CSVWriter(output_dir=tmp_path)

    tweet1 = create_tweet("test_001")
    tweet2 = create_tweet("test_002")
    
    writer.write("test.csv", [tweet1])
    writer.write("test.csv", [tweet1, tweet2])
    
    tweet_ids = read_tweet_ids(tmp_path / "test.csv")
    
    assert len(tweet_ids) == 2
    assert set(tweet_ids) == {"test_001", "test_002"}


def test_write_removes_duplicate_with_new_writer(tmp_path):
    tweet1 = create_tweet("test_001")

    # 一つ目のWriterでCSVに保存
    writer1 = CSVWriter(output_dir=tmp_path)
    writer1.write("test.csv", [tweet1])

    # 新しいWriterを作成して同じ投稿を保存
    writer2 = CSVWriter(output_dir=tmp_path)
    writer2.write("test.csv", [tweet1])

    tweet_ids = read_tweet_ids(tmp_path / "test.csv")

    assert len(tweet_ids) == 1
    assert tweet_ids == ["test_001"]


def test_write_does_nothing_with_empty_list(tmp_path):
    writer = CSVWriter(output_dir=tmp_path)

    writer.write("test.csv", [])

    assert not (tmp_path / "test.csv").exists()


def test_write_tracks_ids_independently_per_file(tmp_path):
    writer = CSVWriter(output_dir=tmp_path)

    tweet1 = create_tweet("test_001")

    writer.write("first.csv", [tweet1])
    writer.write("second.csv", [tweet1])

    first_ids = read_tweet_ids(tmp_path / "first.csv")
    second_ids = read_tweet_ids(tmp_path / "second.csv")

    assert first_ids == ["test_001"]
    assert second_ids == ["test_001"]

# after integration test
def test_write_failure_does_not_register_tweet_ids(tmp_path, monkeypatch):
    writer = CSVWriter(output_dir=tmp_path)

    tweet = create_tweet("tweet_001")

    original_open = Path.open
    should_fail = True

    def mocked_open(path, *args, **kwargs):
        nonlocal should_fail

        if path == tmp_path / "test.csv" and should_fail:
            should_fail = False
            raise OSError("Simulated write failure")

        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", mocked_open)

    # 最初の書き込みは失敗する
    with pytest.raises(OSError):
        writer.write("test.csv", [tweet])

    # 失敗した投稿IDが登録されていないことを確認
    assert "tweet_001" not in writer._known_tweet_ids["test.csv"]

    # 2回目の書き込みは成功する
    writer.write("test.csv", [tweet])

    # CSVに投稿が保存されたことを確認
    csv_path = tmp_path / "test.csv"

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 1
    assert rows[0]["tweet_id"] == "tweet_001"
