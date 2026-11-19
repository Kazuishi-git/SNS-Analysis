import csv
import pytest

from datetime import UTC, datetime
from pathlib import Path

from src.collect.user_writer import UserCSVWriter
from src.collect.models import User


# (1)
def test_get_existing_user_ids_returns_empty_when_file_not_exists(tmp_path):
    # CSVが存在しない場合、空の集合を返すか
    writer = UserCSVWriter(output_dir=tmp_path)

    result = writer.get_existing_user_ids()

    assert result == set()


def test_get_existing_user_ids_loads_ids_from_csv(tmp_path):
    # CSVからIDを読み込めるか
    csv_file = tmp_path / "users.csv"

    with csv_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["author_id", "followers_count"],
        )
        writer.writeheader()
        writer.writerow({
            "author_id": "100",
            "followers_count": 1000,
        })
        writer.writerow({
            "author_id": "200",
            "followers_count": 2000,
        })

    writer = UserCSVWriter(output_dir=tmp_path)

    result = writer.get_existing_user_ids()

    assert result == {"100", "200"}


def test_get_existing_user_ids_ignores_empty_ids(tmp_path):
    # 空のIDを無視できるか
    csv_file = tmp_path / "users.csv"

    with csv_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["author_id", "followers_count"],
        )
        writer.writeheader()
        writer.writerow({
            "author_id": "100",
            "followers_count": 1000,
        })
        writer.writerow({
            "author_id": "",
            "followers_count": 2000,
        })

    writer = UserCSVWriter(output_dir=tmp_path)


    result = writer.get_existing_user_ids()


    assert result == {"100"}


def test_get_existing_user_ids_uses_cache(tmp_path):
    # キャッシュが機能しているか(一度読み込んだIDはキャッシュされ、再読み込みされない)

    csv_file = tmp_path / "users.csv"

    with csv_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["author_id"],
        )
        writer.writeheader()
        writer.writerow({"author_id": "100"})

    writer = UserCSVWriter(output_dir=tmp_path)


    first_result = writer.get_existing_user_ids()

    # CSVに新しいIDを追加する
    with csv_file.open(
        "a",
        newline="",
        encoding="utf-8",
    ) as f:
        csv_writer = csv.DictWriter(
            f,
            fieldnames=["author_id"],
        )
        csv_writer.writerow({"author_id": "200"})

    second_result = writer.get_existing_user_ids()

    assert first_result == {"100"}
    assert second_result == {"100"}
    assert first_result is second_result


# (2)
def create_user(author_id: str) -> User:
    # テスト用のユーザーを作成

    return User(
        author_id=author_id,
        followers_count=100,
        following_count=50,
        tweet_count=200,
        listed_count=10,
        retrieved_at=datetime.now(UTC),
    )


def test_write_creates_csv_and_writes_users(tmp_path):
    # 正常にCSVへ書き込めるか
    writer = UserCSVWriter(output_dir=tmp_path)

    users = [
        create_user("100"),
        create_user("200"),
    ]

    writer.write(users)

    with (tmp_path / "users.csv").open(
        "r",
        newline="",
        encoding="utf-8",
    ) as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 2
    assert {row["author_id"] for row in rows} == {"100", "200"}


def test_write_skips_existing_users(tmp_path):
    # すでにCSVに存在するユーザーを重複保存しないか

    writer = UserCSVWriter(output_dir=tmp_path)

    writer.write([create_user("100")])

    # 新しいインスタンスで既存IDを読み込む
    writer = UserCSVWriter(output_dir=tmp_path)

    writer.write([
        create_user("100"),
        create_user("200"),
    ])

    with (tmp_path / "users.csv").open(
        "r",
        newline="",
        encoding="utf-8",
    ) as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 2
    assert {row["author_id"] for row in rows} == {"100", "200"}


def test_write_skips_duplicate_ids_in_input(tmp_path):
    # 同じリスト内に重複IDがあっても1回だけ保存するか

    writer = UserCSVWriter(output_dir=tmp_path)

    users = [
        create_user("100"),
        create_user("100"),
        create_user("200"),
    ]

    writer.write(users)

    with (tmp_path / "users.csv").open(
        "r",
        newline="",
        encoding="utf-8",
    ) as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 2
    assert {row["author_id"] for row in rows} == {"100", "200"}


def test_write_does_nothing_when_users_is_empty(tmp_path):
    # 空リストの場合はCSVを作成しないか

    writer = UserCSVWriter(output_dir=tmp_path)

    writer.write([])

    assert not (tmp_path / "users.csv").exists()


# (3)
def test_write_does_not_register_ids_when_write_fails(tmp_path,monkeypatch):
    # 書き込み失敗後に再試行できるか

    writer = UserCSVWriter(output_dir=tmp_path)
    users = [create_user("100")]

    original_open = Path.open
    failed = False

    def mock_open(self, *args, **kwargs):
        nonlocal failed

        if self == writer.csv_path and not failed:
            failed = True
            raise OSError("Test write error")

        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", mock_open)

    # 1回目は書き込みに失敗する
    with pytest.raises(OSError, match="Test write error"):
        writer.write(users)

    # 2回目は正常に書き込める
    writer.write(users)

    with writer.csv_path.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as f:
        rows = list(csv.DictReader(f))

    # 最終的にID100が1件だけ存在する
    assert len(rows) == 1
    assert rows[0]["author_id"] == "100"