""" Test """

import pandas as pd
import pytest

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