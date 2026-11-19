""" Test """

import pandas as pd
import pytest

from src.analysis import influencer_profile as profile

from src.analysis.influencer_profile import (
    analyze_post_metrics,
    analyze_user_metrics,
    analyze_overall_metrics,
    analyze_daily_metrics,
    analyze_event_metrics,
)


@pytest.fixture
def sample_posts() -> pd.DataFrame:
    """ Create sample posts for testing """

    return pd.DataFrame(
        [
            {
                "event_id": "starbucks_new_20260717",
                "tweet_id": "A",
                "author_id": "U1",
                "likes": 10,
                "retweets": 2,
                "replies": 1,
                "quotes": 0,
            },
            {
                "event_id": "starbucks_new_20260717",
                "tweet_id": "B",
                "author_id": "U1",
                "likes": 20,
                "retweets": 1,
                "replies": 0,
                "quotes": 1,
            },
            {
                "event_id": "starbucks_new_20260718",
                "tweet_id": "C",
                "author_id": "U2",
                "likes": 5,
                "retweets": 0,
                "replies": 0,
                "quotes": 0,
            },
            {
                "event_id": "starbucks_new_20260901",
                "tweet_id": "D",
                "author_id": "U3",
                "likes": 100,
                "retweets": 10,
                "replies": 2,
                "quotes": 3,
            },
        ]
    )


def test_analysis_post_metrics(sample_posts):
    """ Test post-level descriptive statistics """

    result = analyze_post_metrics(sample_posts)

    assert result.loc["mean", "likes"] == pytest.approx(33.75)
    assert result.loc["50%", "likes"] == pytest.approx(15.0)


def test_analysis_user_metrics(sample_posts):
    """ Test user-level engagement aggregation """

    result = analyze_user_metrics(sample_posts)

    assert len(result) == 3

    user_u1 = result[result["author_id"] == "U1"].iloc[0]

    assert user_u1["post_count"] == 2
    assert user_u1["avg_likes"] == pytest.approx(15.0)
    assert user_u1["total_likes"] == 30
    assert user_u1["total_retweets"] == 3


def test_analysis_overall_metrics(sample_posts):
    """ Test overall engagement aggregation """

    result = analyze_overall_metrics(sample_posts)

    assert len(result) == 1

    row = result.iloc[0]

    assert row["post_count"] == 4
    assert row["unique_users"] == 3
    assert row["total_engagement"] == 155
    assert row["avg_engagement"] == pytest.approx(38.75)

def test_analyze_daily_metrics(sample_posts):
    """ Test daily engagement aggregation."""

    result = analyze_daily_metrics(sample_posts)

    assert len(result) == 3

    july_17 = result[
        result["event_id"] == "starbucks_new_20260717"
    ].iloc[0]

    assert july_17["post_count"] == 2
    assert july_17["unique_users"] == 1
    assert july_17["avg_likes"] == pytest.approx(15.0)


def test_analyze_event_metrics(sample_posts):
    """ Test product-event engagement aggregation."""

    result = analyze_event_metrics(sample_posts)

    assert len(result) == 2

    july = result[
        result["product_event"] == "starbucks_july_2026"
    ].iloc[0]

    september = result[
        result["product_event"] == "starbucks_september_2026"
    ].iloc[0]

    assert july["post_count"] == 3
    assert july["unique_users"] == 2
    assert july["total_engagement"] == 40

    assert september["post_count"] == 1
    assert september["unique_users"] == 1
    assert september["total_engagement"] == 115


def test_analysis_event_metrics_with_unknown_event(sample_posts):
    """ Test that unknown event IDs raise an error """

    invalid_posts = sample_posts.copy()
    invalid_posts.loc[0, "event_id"] = "unknown_event"

    with pytest.raises(ValueError, match="(?i)unknown event IDs"):
        analyze_event_metrics(invalid_posts)

print("="*10 + "ここまで1回目のサンプルのテスト" + "="*10)

def test_empty_posts():
    """ Test that empty posts raise an error"""

    empty_posts = pd.DataFrame(
        columns=[
            "event_id",
            "tweet_id",
            "author_id",
            "likes",
            "retweets",
            "replies",
            "quotes",
        ]
    )

    with pytest.raises(ValueError, match="empty"):
        analyze_overall_metrics(empty_posts)


def test_missing_values(sample_posts):
    """ Test that missing values raise an error"""

    invalid_posts = sample_posts.copy()
    invalid_posts.loc[0, "likes"] = None

    with pytest.raises(ValueError, match="Missing values"):
        analyze_overall_metrics(invalid_posts)


def test_duplicate_tweet_ids(sample_posts):
    """ Test that duplicate tweet IDs raise an error"""

    invalid_posts = pd.concat(
        [sample_posts, sample_posts.iloc[[0]]],
        ignore_index=True,
    )

    with pytest.raises(ValueError, match="Duplicate tweet IDs"):
        analyze_overall_metrics(invalid_posts)


def test_single_post(sample_posts):
    """ Test that a single post can be analyzed"""

    single_post = sample_posts.iloc[[0]].copy()

    result = analyze_overall_metrics(single_post)

    assert result.iloc[0]["post_count"] == 1
    assert result.iloc[0]["unique_users"] == 1
    assert result.iloc[0]["total_engagement"] == 13
    assert result.iloc[0]["avg_engagement"] == pytest.approx(13.0)


# After test coverage(It showed 67%)
def test_load_posts_raises_error_when_no_csv_files(tmp_path, monkeypatch):
    """ Test that an error is raised when no CSV files exist. """

    monkeypatch.setattr(
        profile,
        "RAW_DATA_DIR",
        tmp_path
    )

    with pytest.raises(FileNotFoundError):
        profile.load_posts()


def test_load_posts_combines_multiple_csv_files(tmp_path, monkeypatch, sample_posts):
    """ Test that multiple CSV files are combined correctly. """

    monkeypatch.setattr(
        profile,
        "RAW_DATA_DIR",
        tmp_path
    )

    # CSVファイルを2つ作成
    sample_posts.iloc[:2].to_csv(  #先頭2行
        tmp_path / "posts_1.csv",
        index=False
    )

    sample_posts.iloc[2:].to_csv(  # 3行目以降
        tmp_path / "posts_2.csv",
        index=False
    )

    result = profile.load_posts()

    assert len(result) == 4
    assert set(result["tweet_id"]) == {"A", "B", "C", "D"}
    assert result["author_id"].nunique() == 3

def test_missing_required_columns(sample_posts):
    """ Test that missing required columns raise an error. """

    invalid_posts = sample_posts.drop(columns=["quotes"])

    with pytest.raises(
        ValueError,
        match="Missing required columns"
    ):
        analyze_overall_metrics(invalid_posts)



# test for main
def test_main_creates_output_files(tmp_path, monkeypatch, sample_posts):

    """ Test that main creates all expected output files. """

    # 出力先をテスト用ディレクトリに変更
    monkeypatch.setattr(
        profile,
        "OUTPUT_DIR",
        tmp_path
    )

    # サンプルデータを読み込ませる
    monkeypatch.setattr(
        profile,
        "load_posts",
        lambda: sample_posts.copy()
    )

    # main() を実行
    profile.main()

    expected_files = [
        "post_metrics.csv",
        "user_metrics.csv",
        "daily_metrics.csv",
        "overall_metrics.csv",
        "event_metrics.csv"
    ]

    for filename in expected_files:
        assert (tmp_path / filename).exists()

def test_main_propagates_load_posts_error(tmp_path, monkeypatch):
    """ Test that main propagates loading errors. """

    monkeypatch.setattr(
        profile,
        "OUTPUT_DIR",
        tmp_path
    )

    def mock_load_posts():
        raise FileNotFoundError("No CSV files found.")

    monkeypatch.setattr(
        profile,
        "load_posts",
        mock_load_posts
    )

    with pytest.raises(FileNotFoundError):
        profile.main()


def test_main_saves_correct_overall_metrics(tmp_path, monkeypatch, sample_posts):
    """ Test that main saves correct overall metrics. """

    monkeypatch.setattr(
        profile,
        "OUTPUT_DIR",
        tmp_path
    )

    monkeypatch.setattr(
        profile,
        "load_posts",
        lambda: sample_posts.copy()
    )

    profile.main()

    result = pd.read_csv(tmp_path / "overall_metrics.csv")

    assert len(result) == 1

    row = result.iloc[0]

    assert row["post_count"] == 4
    assert row["unique_users"] == 3
    assert row["total_engagement"] == 155
    assert row["avg_engagement"] == pytest.approx(38.75)