""" Integration Test """

import csv
import json
import pytest

from datetime import datetime, UTC
from types import SimpleNamespace
from unittest.mock import Mock
from tweepy.errors import TweepyException

import src.collect.x_posts as collector_module

from src.collect.x_posts import XPostCollector
from src.collect.models import Event
from src.collect.writer import CSVWriter
from src.collect.state import StateManager


def create_event() -> Event:
    return Event(
        event_id="integration_test",
        query="スタバ 新作",
        start_time=datetime(2026, 11, 1, tzinfo=UTC),
        end_time=datetime(2026, 11, 2, tzinfo=UTC),
        max_tweet=200,
    )


def create_post(tweet_id: str):
    return SimpleNamespace(
        id=tweet_id,
        author_id="user_001",
        created_at=datetime(2026, 11, 1, tzinfo=UTC),
        text=f"テスト投稿 {tweet_id}",
        public_metrics={
            "like_count": 10,
            "retweet_count": 2,
            "reply_count": 1,
            "quote_count": 0,
        },
    )


def create_collector(tmp_path, monkeypatch):
    # API通信だけMockに置き換える
    mock_client = Mock()

    monkeypatch.setattr(
        collector_module,
        "XClient",
        lambda: mock_client,
    )

    # CSVWriterとStateManagerは実物を使用
    monkeypatch.setattr(
        collector_module,
        "CSVWriter",
        # RAW_DATA_DIRではなく、一時的な保存先にCSVを作成
        lambda: CSVWriter(output_dir=tmp_path / "raw"), # pytestが用意する一時ディレクトリ
    )

    monkeypatch.setattr(
        collector_module,
        "StateManager",
        # チェクポイントも一時保存
        lambda: StateManager(state_file=tmp_path / "state.json"),
    )

    collector = XPostCollector()

    return collector, mock_client

# 1
def test_integration_collect_saves_csv_and_checkpoint(tmp_path,monkeypatch):

    collector, mock_client = create_collector(
        tmp_path,
        monkeypatch,
    )

    event = create_event()

    # APIレスポンスを模擬
    mock_client.search_posts.return_value = SimpleNamespace(
        data=[
            create_post("tweet_001"),
            create_post("tweet_002"),
        ],
        meta={"next_token": None},
    )

    # 収集処理を実行（最後まで実行できるか）
    collector.collect(event)

    # CSVファイルの確認
    csv_path = tmp_path / "raw" / "integration_test.csv"

    # CSVが正しく作成されたか
    assert csv_path.exists()

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 2
    assert rows[0]["tweet_id"] == "tweet_001"
    assert rows[1]["tweet_id"] == "tweet_002"

    # チェックポイントの確認
    state_path = tmp_path / "state.json"

    assert state_path.exists()

    with state_path.open("r", encoding="utf-8") as f:
        state = json.load(f)

    # チェックポイントが正しく保存されたか
    assert state["event_id"] == event.event_id
    assert state["next_token"] is None
    assert "updated_at" in state

# 2
def test_integration_collect_multiple_pages(tmp_path, monkeypatch):
    collector, mock_client = create_collector(tmp_path, monkeypatch)
    event = create_event()

    # 1ページ目：2件取得し、次ページのトークンを返す
    first_response = SimpleNamespace(
        data=[
            create_post("tweet_001"),
            create_post("tweet_002"),
        ],
        meta={"next_token": "page_2_token"},
    )

    # 2ページ目：1件取得して終了
    second_response = SimpleNamespace(
        data=[
            create_post("tweet_003"),
        ],
        meta={"next_token": None},
    )

    mock_client.search_posts.side_effect = [
        first_response,
        second_response,
    ]

    collector.collect(event)

    # CSVの保存内容を確認
    csv_path = tmp_path / "raw" / "integration_test.csv"

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 3
    assert [row["tweet_id"] for row in rows] == [
        "tweet_001",
        "tweet_002",
        "tweet_003",
    ]

    # APIが2回呼び出されたことを確認
    assert mock_client.search_posts.call_count == 2

    # 2回目のAPI呼び出しに次ページのトークンが渡されたことを確認
    calls = mock_client.search_posts.call_args_list

    assert calls[0].kwargs["next_token"] is None
    assert calls[1].kwargs["next_token"] == "page_2_token"

    # 最終チェックポイントを確認
    state_path = tmp_path / "state.json"

    with state_path.open("r", encoding="utf-8") as f:
        state = json.load(f)

    assert state["event_id"] == event.event_id
    assert state["next_token"] is None


# 3
def test_integration_resume_after_api_error(tmp_path, monkeypatch):
    event = create_event()

    # 1回目のCollectorを作成
    collector, mock_client = create_collector(tmp_path, monkeypatch)

    first_response = SimpleNamespace(
        data=[
            create_post("tweet_001"),
            create_post("tweet_002"),
        ],
        meta={"next_token": "page_2_token"},
    )

    # 1ページ目は成功、2ページ目でAPIエラー
    mock_client.search_posts.side_effect = [
        first_response,
        TweepyException("temporary API error"),
    ]

    with pytest.raises(TweepyException):
        collector.collect(event)

    # 1ページ目のデータが保存されていることを確認
    csv_path = tmp_path / "raw" / "integration_test.csv"

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 2

    # チェックポイントが保存されていることを確認
    state_path = tmp_path / "state.json"

    with state_path.open("r", encoding="utf-8") as f:
        state = json.load(f)

    assert state["next_token"] == "page_2_token"

    # 新しいCollectorを作成して収集を再開
    resumed_collector, resumed_client = create_collector(
        tmp_path, monkeypatch
    )

    second_response = SimpleNamespace(
        data=[create_post("tweet_003")],
        meta={"next_token": None},
    )

    resumed_client.search_posts.return_value = second_response

    resumed_collector.collect(event)

    # 保存済みデータと再開後のデータを確認
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 3
    assert [row["tweet_id"] for row in rows] == [
        "tweet_001",
        "tweet_002",
        "tweet_003",
    ]

    # 保存済みのトークンから再開したことを確認
    resumed_client.search_posts.assert_called_once()

    call_kwargs = resumed_client.search_posts.call_args.kwargs
    assert call_kwargs["next_token"] == "page_2_token"

    # 最終チェックポイントを確認
    with state_path.open("r", encoding="utf-8") as f:
        state = json.load(f)

    assert state["next_token"] is None

# 4
def test_integration_collect_removes_duplicate_tweets(
    tmp_path, monkeypatch
):
    collector, mock_client = create_collector(tmp_path, monkeypatch)
    event = create_event()

    first_response = SimpleNamespace(
        data=[
            create_post("tweet_001"),
            create_post("tweet_002"),
        ],
        meta={"next_token": "page_2_token"},
    )

    second_response = SimpleNamespace(
        data=[
            create_post("tweet_002"),
            create_post("tweet_003"),
        ],
        meta={"next_token": None},
    )

    mock_client.search_posts.side_effect = [
        first_response,
        second_response,
    ]

    collector.collect(event)

    # CSVの内容を確認
    csv_path = tmp_path / "raw" / "integration_test.csv"

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    tweet_ids = [row["tweet_id"] for row in rows]

    # 重複が排除され、3件だけ保存されている
    assert len(rows) == 3
    assert tweet_ids == [
        "tweet_001",
        "tweet_002",
        "tweet_003",
    ]

    # APIは2ページ分呼び出されている
    assert mock_client.search_posts.call_count == 2
