from datetime import datetime, UTC
from types import SimpleNamespace
from unittest.mock import Mock

import src.collect.x_posts as collector_module

from src.collect.x_posts import XPostCollector
from src.collect.models import Event


def create_event() -> Event:
    return Event(
        event_id="test_event",
        query="スタバ 新作",
        start_time=datetime(2026, 11, 1, tzinfo=UTC),
        end_time=datetime(2026, 11, 2, tzinfo=UTC),
        max_tweet=200,
    )

def create_collector(monkeypatch):
    mock_client = Mock()
    mock_writer = Mock()
    mock_state = Mock()

    monkeypatch.setattr(
        collector_module,
        "XClient",
        Mock(return_value=mock_client),
    )
    monkeypatch.setattr(
        collector_module,
        "CSVWriter",
        Mock(return_value=mock_writer),
    )
    monkeypatch.setattr(
        collector_module,
        "StateManager",
        Mock(return_value=mock_state),
    )

    collector = XPostCollector()

    return collector, mock_client, mock_writer, mock_state


def create_post(tweet_id : str):
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

def create_response(tweet_ids: list[str], next_token=None):
    return SimpleNamespace(
        data=[create_post(tweet_id) for tweet_id in tweet_ids],
        meta = {"next_token": next_token}
    )

def test_convert_response_convert_tweets(monkeypatch):
    # データ変換、APIレスポンスがTweet（post）に正しく変換される
    collector, _, _, _ = create_collector(monkeypatch)

    created_at = datetime(2026, 11, 1, tzinfo=UTC)

    post = SimpleNamespace(
        id="tweet_001",
        author_id="user_001",
        created_at=created_at,
        text="スタバの新作を飲みました",
        public_metrics={
            "like_count": 100,
            "retweet_count": 20,
            "reply_count": 5,
            "quote_count": 3,
        },
    )

    response = SimpleNamespace(data=[post])

    tweets = collector._convert_response(
        event=create_event(),
        response=response,
    )

    assert len(tweets) == 1

    tweet = tweets[0]

    assert tweet.event_id == "test_event"
    assert tweet.tweet_id == "tweet_001"
    assert tweet.author_id == "user_001"
    assert tweet.created_at == created_at
    assert tweet.text == "スタバの新作を飲みました"
    assert tweet.likes == 100
    assert tweet.retweets == 20
    assert tweet.replies == 5
    assert tweet.quotes == 3

def test_convert_response_returns_empty_list_when_no_data(monkeypatch):
    # 空データ、投稿がない場合に空リストを返す
    collector, _, _, _ = create_collector(monkeypatch)

    response = SimpleNamespace(data=None)

    tweets = collector._convert_response(
        event=create_event(),
        response=response,
    )

    assert tweets == []


def test_collect_saves_posts_and_checkpoint(monkeypatch):
    # 取得した投稿が保存され、正常終了されるか
    # また、各ページ取得後に状態が保存されるか
    collector, mock_client, mock_writer, mock_state = create_collector(monkeypatch)

    event = create_event()
    response = create_response(["tweet_001", "tweet_002"])

    mock_client.search_posts.return_value = response
    mock_state.load.return_value = None

    collector.collect(event)

    mock_client.search_posts.assert_called_once_with(
        event=event,
        next_token=None,
    )

    mock_writer.write.assert_called_once()

    saved_tweets = mock_writer.write.call_args.kwargs["tweets"]

    assert len(saved_tweets) == 2
    assert saved_tweets[0].tweet_id == "tweet_001"
    assert saved_tweets[1].tweet_id == "tweet_002"

    mock_state.save.assert_called_once()

    saved_state = mock_state.save.call_args.args[0]

    assert saved_state["event_id"] == event.event_id
    assert saved_state["next_token"] is None
    assert "updated_at" in saved_state

def test_collect_fetches_multiple_pages(monkeypatch):
    # next_tokenを用いて次のページを取得できるか
    collector, mock_client, mock_writer, mock_state = create_collector(monkeypatch)

    event = create_event()

    first_response = create_response(
        ["tweet_001", "tweet_002"],
        next_token="page_2_token",
    )
    second_response = create_response(
        ["tweet_003"],
    )

    # ページェネーションの再現
    mock_client.search_posts.side_effect = [
        first_response,
        second_response,
    ]
    mock_state.load.return_value = None

    collector.collect(event)

    assert mock_client.search_posts.call_count == 2

    calls = mock_client.search_posts.call_args_list

    assert calls[0].kwargs["next_token"] is None
    assert calls[1].kwargs["next_token"] == "page_2_token"

    assert mock_writer.write.call_count == 2
    assert mock_state.save.call_count == 2

def test_collect_resumes_from_saved_token(monkeypatch):
    # 保存済みnext_tokenから再開できるか
    collector, mock_client, _, mock_state = create_collector(monkeypatch)

    event = create_event()

    # 前回保存した状態の再現
    mock_state.load.return_value = {
        "event_id": event.event_id,
        "next_token": "resume_token",
    }

    mock_client.search_posts.return_value = create_response(
        ["tweet_003"],
    )

    collector.collect(event)

    mock_client.search_posts.assert_called_once_with(
        event=event,
        next_token="resume_token",
    )


def test_collect_stops_at_max_tweet(monkeypatch):
    # max_tweetを超える投稿を保存しないか
    collector, mock_client, mock_writer, mock_state = create_collector(monkeypatch)

    event = create_event()
    event.max_tweet = 2

    response = create_response(
        ["tweet_001", "tweet_002", "tweet_003"],
        next_token="page_2_token",
    )

    mock_client.search_posts.return_value = response
    mock_state.load.return_value = None

    collector.collect(event)

    mock_client.search_posts.assert_called_once()

    mock_writer.write.assert_called_once()

    saved_tweets = mock_writer.write.call_args.kwargs["tweets"]

    assert len(saved_tweets) == 2
    assert [tweet.tweet_id for tweet in saved_tweets] == [
        "tweet_001",
        "tweet_002",
    ]

    saved_state = mock_state.save.call_args.args[0]

    assert saved_state["next_token"] == "page_2_token"
