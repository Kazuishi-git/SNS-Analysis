import pytest

from unittest.mock import Mock, call
from datetime import UTC, datetime
from types import SimpleNamespace

from tweepy.errors import TweepyException

from src.collect.user_collector import XUserCollector
from src.collect.models import User



# (1)
def test_load_user_ids_returns_unique_sorted_ids(tmp_path,monkeypatch):
    # CSVからauthor_idを取得できるか

    # テスト用CSVファイルを作成
    csv_content = (
        "tweet_id,author_id,text\n"
        "001,100,user A\n"
        "002,200,user B\n"
        "003,100,user C\n"
    )

    csv_file = tmp_path / "posts.csv"
    csv_file.write_text(csv_content, encoding="utf-8")

    # テスト中のみRAW_DATA_DIRを一時ディレクトリに差し替える、今回はテスト環境で指定できるかトライ
    monkeypatch.setattr(
        "src.collect.user_collector.RAW_DATA_DIR",
        tmp_path,
    )

    # ユーザーIDを読み込む
    collector = XUserCollector()
    result = collector._load_user_ids()

    # 重複がなく、昇順で取得できる
    assert result == ["100", "200"]


def test_load_user_ids_reads_multiple_csv_files(tmp_path, monkeypatch):
    # 複数の投稿に同じIDがあっても一つにまとめる

    # 複数のCSVファイルを作成
    csv1 = tmp_path / "posts_1.csv"
    csv2 = tmp_path / "posts_2.csv"

    csv1.write_text(
        "tweet_id,author_id\n001,100\n002,200\n",
        encoding="utf-8",
    )
    csv2.write_text(
        "tweet_id,author_id\n003,300\n004,200\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "src.collect.user_collector.RAW_DATA_DIR",
        tmp_path,
    )
    
    collector = XUserCollector()
    result = collector._load_user_ids()

    assert result == ["100", "200", "300"]


def test_load_user_ids_ignores_empty_author_ids(tmp_path, monkeypatch):
    # 複数のCSVからIDを取得できるか

    # author_idが空の行を含むCSV
    csv_file = tmp_path / "posts.csv"
    csv_file.write_text(
        "tweet_id,author_id\n001,100\n002,\n003,200\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "src.collect.user_collector.RAW_DATA_DIR",
        tmp_path,
    )

    collector = XUserCollector()
    result = collector._load_user_ids()

    assert result == ["100", "200"]


def test_load_user_ids_raises_error_when_no_csv_files(tmp_path,monkeypatch):
    # CSvファイルが一つもない場合にErrorを吐けるか
    
    # CSVファイルが存在しないディレクトリ
    monkeypatch.setattr(
        "src.collect.user_collector.RAW_DATA_DIR",
        tmp_path,
    )

    collector = XUserCollector()

    with pytest.raises(FileNotFoundError):
        collector._load_user_ids()


# (2)
def test_get_new_user_ids_excludes_existing_ids():
    # 未保存IDだけ返すか

    collector = XUserCollector()
    collector.writer = Mock()
    collector.writer.get_existing_user_ids.return_value = {
        "200",
        "400",
    }

    user_ids = ["100", "200", "300", "400"]

    result = collector._get_new_user_ids(user_ids)

    assert result == ["100", "300"]
    collector.writer.get_existing_user_ids.assert_called_once()


def test_get_new_user_ids_returns_empty_when_all_exist():
    # 全IDが保存済みで、空か

    collector = XUserCollector()
    collector.writer = Mock()
    collector.writer.get_existing_user_ids.return_value = {
        "100",
        "200",
    }

    user_ids = ["100", "200"]

    result = collector._get_new_user_ids(user_ids)

    assert result == []


def test_get_new_user_ids_returns_all_when_none_exist():
    # 入力IDを全て返すか
   
    collector = XUserCollector()
    collector.writer = Mock()
    collector.writer.get_existing_user_ids.return_value = set()

    user_ids = ["100", "200", "300"]

    result = collector._get_new_user_ids(user_ids)

    assert result == ["100", "200", "300"]


def test_get_new_user_ids_returns_empty_when_input_is_empty():
    # 空リストを渡し、空リストが帰ってくるか
    collector = XUserCollector()
    collector.writer = Mock()
    collector.writer.get_existing_user_ids.return_value = set()

    user_ids = []

    result = collector._get_new_user_ids(user_ids)

    assert result == []


# (3)
def test_convert_response_converts_user_data():
    # ユーザ情報が正しく変換されている
 
    collector = XUserCollector()

    api_user = SimpleNamespace(
        id="100",
        public_metrics={
            "followers_count": 1000,
            "following_count": 200,
            "tweet_count": 500,
            "listed_count": 10,
        },
    )

    response = Mock()
    response.data = [api_user]

    result = collector._convert_response(response)

    assert len(result) == 1
    assert isinstance(result[0], User)

    user = result[0]
    assert user.author_id == "100"
    assert user.followers_count == 1000
    assert user.following_count == 200
    assert user.tweet_count == 500
    assert user.listed_count == 10

    assert isinstance(user.retrieved_at, datetime)
    assert user.retrieved_at.tzinfo == UTC


def test_convert_response_converts_multiple_users():
    # 複数版

    collector = XUserCollector()

    api_users = [
        SimpleNamespace(
            id="100",
            public_metrics={
                "followers_count": 100,
                "following_count": 20,
                "tweet_count": 50,
                "listed_count": 1
            },
        ),
        SimpleNamespace(
            id="200",
            public_metrics={
                "followers_count": 200,
                "following_count": 40,
                "tweet_count": 100,
                "listed_count": 2
            },
        ),
    ]

    response = Mock()
    response.data = api_users

  
    result = collector._convert_response(response)


    assert len(result) == 2
    assert [user.author_id for user in result] == ["100", "200"]
    assert result[0].followers_count == 100
    assert result[1].followers_count == 200


def test_convert_response_returns_empty_when_data_is_none():
    # 空リストを返すか（response is None）

    collector = XUserCollector()

    response = Mock()
    response.data = None

    result = collector._convert_response(response)

    assert result == []


def test_convert_response_skips_user_without_public_metrics():
    # スキップするか

    collector = XUserCollector()

    api_users = [
        SimpleNamespace(
            id="100",
            public_metrics={
                "followers_count": 100,
                "following_count": 20,
                "tweet_count": 50,
                "listed_count": 1
            },
        ),
        SimpleNamespace(
            id="200",
            public_metrics=None,
        ),
    ]

    response = Mock()
    response.data = api_users

    result = collector._convert_response(response)

    assert len(result) == 1
    assert result[0].author_id == "100"


def test_convert_response_returns_empty_when_all_metrics_are_none():
  
    collector = XUserCollector()

    api_users = [
        SimpleNamespace(id="100", public_metrics=None),
        SimpleNamespace(id="200", public_metrics=None)
    ]

    response = Mock()
    response.data = api_users

    result = collector._convert_response(response)

    assert result == []


(4)
def test_collect_users_collects_and_saves_users():
    # 取得したユーザ情報が保存される

    collector = XUserCollector()
    collector.client = Mock()
    collector.writer = Mock()

    response = Mock()
    users = [Mock(), Mock()]
    collector.client.get_users.return_value = response
    collector._convert_response = Mock(return_value=users)

    user_ids = ["100", "200"]

    collector._collect_users(user_ids)

    collector.client.get_users.assert_called_once_with(user_ids)
    collector._convert_response.assert_called_once_with(response)
    collector.writer.write.assert_called_once_with(users)


def test_collect_users_splits_ids_into_batches():
    
    collector = XUserCollector()
    collector.client = Mock()
    collector.writer = Mock()
    collector._convert_response = Mock(return_value=[])

    user_ids = [str(i) for i in range(250)]

    collector._collect_users(user_ids)

    assert collector.client.get_users.call_count == 3

    assert collector.client.get_users.call_args_list == [
        # 100未満：１回のAPI呼び出しで処理されるか
        call(user_ids[:100]),
        # 100件超過：100件ずつ分割されるか
        call(user_ids[100:200]),
        call(user_ids[200:])
    ]

    assert collector.writer.write.call_count == 3


def test_collect_users_handles_exact_batch_size():
    # 上記の100件ちょうどのとき：余計なAPI呼び出しが発生しないか

    collector = XUserCollector()
    collector.client = Mock()
    collector.writer = Mock()
    collector._convert_response = Mock(return_value=[])

    user_ids = [str(i) for i in range(100)]

    collector._collect_users(user_ids)

    collector.client.get_users.assert_called_once_with(user_ids)
    collector.writer.write.assert_called_once()


def test_collect_users_does_nothing_when_ids_are_empty():
    # 空リストのとき、APIを呼び出さず終了するか

    collector = XUserCollector()
    collector.client = Mock()
    collector.writer = Mock()

    user_ids = []

    collector._collect_users(user_ids)

    collector.client.get_users.assert_not_called()
    collector.writer.write.assert_not_called()


def test_collect_users_reraises_api_error():
    # 例外を再送出し、保存処理を行わない

    collector = XUserCollector()
    collector.client = Mock()
    collector.writer = Mock()

    collector.client.get_users.side_effect = TweepyException(
        "API request failed"
    )

    user_ids = ["100", "200"]

    with pytest.raises(TweepyException):
        collector._collect_users(user_ids)

    collector.writer.write.assert_not_called()



# last
def test_collect_runs_full_workflow():
    # ID取得から新規ユーザ収集まで順番に実行されるか

    collector = XUserCollector()

    all_user_ids = ["100", "200", "300"]
    new_user_ids = ["200", "300"]

    collector._load_user_ids = Mock(return_value=all_user_ids)
    collector._get_new_user_ids = Mock(return_value=new_user_ids)
    collector._collect_users = Mock()

    collector.collect()

    collector._load_user_ids.assert_called_once_with()
    collector._get_new_user_ids.assert_called_once_with(all_user_ids)
    collector._collect_users.assert_called_once_with(new_user_ids)


def test_collect_stops_when_no_new_users():
    # 新規ユーザなし：collect_usersが呼ばれず終了するか
    collector = XUserCollector()

    all_user_ids = ["100", "200"]

    collector._load_user_ids = Mock(return_value=all_user_ids)
    collector._get_new_user_ids = Mock(return_value=[])
    collector._collect_users = Mock()

    collector.collect()

    collector._load_user_ids.assert_called_once_with()
    collector._get_new_user_ids.assert_called_once_with(all_user_ids)
    collector._collect_users.assert_not_called()


def test_collect_reraises_error_when_loading_user_ids_fails():
    # CSVファイルなし：load_usr_idsの例外はどうなるか

    collector = XUserCollector()

    collector._load_user_ids = Mock(
        side_effect=FileNotFoundError("CSV file not found")
    )
    collector._get_new_user_ids = Mock()
    collector._collect_users = Mock()

    with pytest.raises(FileNotFoundError):
        collector.collect()

    collector._get_new_user_ids.assert_not_called()
    collector._collect_users.assert_not_called()


def test_collect_reraises_api_error():
    # APIエラー：collect_usersの例外はどうなる
    
    collector = XUserCollector()

    all_user_ids = ["100", "200"]
    new_user_ids = ["100", "200"]

    collector._load_user_ids = Mock(return_value=all_user_ids)
    collector._get_new_user_ids = Mock(return_value=new_user_ids)
    collector._collect_users = Mock(
        side_effect=TweepyException("API request failed")
    )

    # Act & Assert
    with pytest.raises(TweepyException):
        collector.collect()

    collector._load_user_ids.assert_called_once_with()
    collector._get_new_user_ids.assert_called_once_with(all_user_ids)
    collector._collect_users.assert_called_once_with(new_user_ids)