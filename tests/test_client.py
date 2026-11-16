import pytest
from unittest.mock import Mock
from datetime import datetime, UTC

import src.collect.client as client_module

from src.collect.client import XClient
from src.collect.models import Event
from tweepy.errors import TweepyException

def create_event() -> Event:
    return Event(
        event_id="test_event",
        query="スタバ 新作",
        start_time=datetime(2026, 11, 1, tzinfo=UTC),
        end_time=datetime(2026, 11, 2, tzinfo=UTC),
        max_tweet=200,
    )

def create_x_client(monkeypatch):
    mock_api = Mock()

    # TweepyのClientをモックに置き換える
    mock_client_class = Mock(return_value=mock_api)
    monkeypatch.setattr(
        client_module,
        "Client",
        mock_client_class,
    )

    x_client = XClient()

    return x_client, mock_api, mock_client_class

def test_init_creates_tweepy_client(monkeypatch):
    # 初期化、APIクライアントが正しい設定で生成される
    _, _, mock_client_class = create_x_client(monkeypatch) #  _,は受け取った値を使わないことを示す

    mock_client_class.assert_called_once()

    kwargs = mock_client_class.call_args.kwargs

    assert "bearer_token" in kwargs
    assert kwargs["wait_on_rate_limit"] is True

def test_search_posts_calls_api_with_correct_arguments(monkeypatch):
    # 投稿取得、search_all_tweets()に正しい引数が渡される
    x_client, mock_api, _ = create_x_client(monkeypatch)

    event = create_event()
    expected_response = Mock()
    mock_api.search_all_tweets.return_value = expected_response

    response = x_client.search_posts(event)

    mock_api.search_all_tweets.assert_called_once_with(
        query=event.query,
        start_time=event.start_time,
        end_time=event.end_time,
        tweet_fields=XClient.DEFAULT_TWEET_FIELDS,
        max_results=XClient.DEFAULT_MAX_RESULT,
        next_token=None,
    )

    assert response is expected_response

def test_search_posts_passes_next_token(monkeypatch):
    # ページネーション、next_tokenが正しく渡される
    x_client, mock_api, _ = create_x_client(monkeypatch)

    event = create_event()
    next_token = "next_page_token"

    expected_response = Mock()
    mock_api.search_all_tweets.return_value = expected_response

    response = x_client.search_posts(
        event,
        next_token=next_token,
    )

    assert response is expected_response

    assert mock_api.search_all_tweets.call_args.kwargs["next_token"] == next_token


def test_get_users_calls_api_with_correct_arguments(monkeypatch):
    # ユーザ取得、get_users()に正しいIDとフィールドが渡される
    x_client, mock_api, _ = create_x_client(monkeypatch)

    user_ids = ["user_001", "user_002"]
    expected_response = Mock()
    mock_api.get_users.return_value = expected_response

    response = x_client.get_users(user_ids)

    mock_api.get_users.assert_called_once_with(
        ids=user_ids,
        user_fields=XClient.DEFAULT_USER_FIELDS,
    )

    assert response is expected_response


def test_search_posts_propagates_api_exception(monkeypatch):
    x_client, mock_api, _ = create_x_client(monkeypatch)

    event = create_event()

    mock_api.search_all_tweets.side_effect = TweepyException(
        "API request failed"
    )

    with pytest.raises(TweepyException):
        x_client.search_posts(event)