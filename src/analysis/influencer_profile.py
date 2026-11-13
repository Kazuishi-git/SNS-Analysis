""" Analyze post and user-level engagement metrics."""

from pathlib import Path
import pandas as pd
from src.utils.config import DATA_DIR, RESULT_DIR


RAW_DATA_DIR = DATA_DIR / "raw"
OUTPUT_DIR = RESULT_DIR / "influencer"

EVENT_PERIODS = {
    "starbucks_july_2026" : (
        "20260717",
        "20260727",
    ),
    "starbucks_september_2026" : (
        "20260828",
        "20260907",
    ),
}


def load_posts() -> pd.DataFrame:
    """ Load and combine all daily CSV files. """

    csv_files = sorted(RAW_DATA_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError("No CSV files found in data/raw.")

    dataframes = [pd.read_csv(file) for file in csv_files]
    posts = pd.concat(dataframes, ignore_index=True)

    return posts


def analyze_post_metrics(posts: pd.DataFrame) -> pd.DataFrame:
    """ Calculate descriptive statistics for engagement metrics. """

    metrics = ["likes", "retweets", "replies", "quotes"]

    return posts[metrics].describe(
        percentiles=[0.5, 0.75, 0.90, 0.95, 0.99]
    )

def analyze_user_metrics(posts: pd.DataFrame) -> pd.DataFrame:
    """ Aggregate engagement metrics by author. """

    user_metrics = (
        posts.groupby("author_id")
        .agg(
            post_count=("tweet_id", "count"),
            avg_likes=("likes", "mean"),
            median_likes=("likes", "median"),
            avg_retweets=("retweets", "mean"),
            median_retweets=("retweets", "median"),
            total_likes=("likes", "sum"),
            total_retweets=("retweets", "sum"),
        )
        .reset_index()
    )

    return user_metrics.sort_values(
        "avg_likes", ascending=False
    )

def analyze_daily_metrics(post : pd.DataFrame) -> pd.DataFrame:
    """ Calculate engagement metrics for each day. """

    daily_metrics = (
        post.groupby("event_id")
        .agg(
            post_count=("tweet_id", "count"),
            unique_users=("author_id", "nunique"),
            avg_likes=("likes", "mean"),
            median_likes=("likes", "median"),
            avg_retweets=("retweets", "mean"),
            median_retweets=("retweets", "median"),
        )
        .reset_index()
    )

    return daily_metrics

def aggregate_engagement_metrics(posts : pd.DataFrame) -> pd.DataFrame :
    """ Aggregate engagement metrics for given posts """

    metrics = {
        "post_count": posts["tweet_id"].count(),
        "unique_users": posts["author_id"].nunique(),
        "avg_likes": posts["likes"].mean(),
        "median_likes": posts["likes"].median(),
        "avg_retweets": posts["retweets"].mean(),
        "median_retweets": posts["retweets"].median(),
        "avg_replies": posts["replies"].mean(),
        "median_replies": posts["replies"].median(),
        "avg_quotes": posts["quotes"].mean(),
        "median_quotes": posts["quotes"].median(),
        "total_engagement": posts["total_engagement"].sum(),
        "avg_engagement": posts["total_engagement"].mean(),
    }

    return pd.DataFrame([metrics])

def analyze_overall_metrics(posts : pd.DataFrame) -> pd.DataFrame :
    """ Calculate overall engagement metrics """

    posts = posts.copy()

    posts["total_engagement"] = (
        posts["likes"] + posts["retweets"] + posts["replies"] + posts["quotes"]
    )

    return aggregate_engagement_metrics(posts)

def analyze_event_metrics(posts : pd.DataFrame) -> pd.DataFrame :
    """ Calculate engagement metrics for each product event """

    posts = posts.copy()

    # event_idから日付を抽出
    event_dates = posts["event_id"].str.extract(
        r"(\d{8})$"
    )[0]

    event_dates = pd.to_datetime(
        event_dates,
        format = "%Y%m%d",
        errors = "coerce",
    )

    # イベントの割り当て
    posts["product_event"] = pd.NA

    for event_name, (start_date, end_date) in EVENT_PERIODS.items():
        start = pd.to_datetime(start_date, format="%Y%m%d")
        end = pd.to_datetime(end_date, format="%Y%m%d")

        mask = event_dates.between(start, end)

        posts.loc[mask, "product_event"] = event_name

    # Check unclassified events
    if posts["product_event"].isna().any():
        unknown_events = (
            posts.loc[posts["product_event"].isna(), "event_id"]
            .drop_duplicates()
            .tolist()
        )

        raise ValueError(
            f"unknown event IDs found: {unknown_events}"
        )

    # 総エンゲージメントの集計
    posts["total_engagement"] = (
        posts["likes"] + posts["retweets"] + posts["replies"] + posts["quotes"]
    )

    # イベントごとに集計
    event_results = []

    for event_name, group in posts.groupby("product_event"):
        result = aggregate_engagement_metrics(group)
        result.insert(0, "product_event", event_name)
        event_results.append(result)

    return pd.concat(event_results, ignore_index=True)

def main() -> None:
    """ Run influencer profile analysis. """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    posts = load_posts()

    post_metrics = analyze_post_metrics(posts)
    user_metrics = analyze_user_metrics(posts)

    post_metrics.to_csv(
        OUTPUT_DIR / "post_metrics.csv",
        encoding="utf-8-sig",
    )

    user_metrics.to_csv(
        OUTPUT_DIR / "user_metrics.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # print(f"Total posts: {len(posts)}")
    # print(f"Unique users: {posts['author_id'].nunique()}")
    # print("\nPost-level metrics:")
    # print(post_metrics.to_string())

    # print("\nTop 10 users by average likes:")
    # print(user_metrics.head(10).to_string(index=False))

    # 投稿数別のユーザー数と割合
    post_count_distribution = (
        user_metrics["post_count"]
        .value_counts()
        .sort_index()
        .rename_axis("post_count")
        .reset_index(name="user_count")
    )

    post_count_distribution["percentage"] = (
        post_count_distribution["user_count"] / len(user_metrics) * 100
    )

    # print("\nUsers by post count:")
    # print(post_count_distribution.to_string(index=False))

    # print("\nPosts count statistics:")
    # print(user_metrics["post_count"].describe().to_string())

    # 2件以上（複数回）投稿したユーザー
    active_users = user_metrics[
        user_metrics["post_count"] >= 2
    ].copy()

    active_users = active_users.sort_values(
        "median_likes", ascending=False
    )

    # print("\nTop 10 active users by average likes:")
    # print(active_users.head(10).to_string(index=False))

    # print(f"\nActive users: {len(active_users)}")


    # Daily metrics
    daily_metrics = analyze_daily_metrics(posts)

    daily_metrics.to_csv(
        OUTPUT_DIR / "daily_metrics.csv",
        index=False,
        encoding="utf-8-sig",
    )

    print("\nDaily metrics:")
    print(daily_metrics.to_string(index=False))

    # Overall metrics
    Overall_metrics = analyze_overall_metrics(posts)

    Overall_metrics.to_csv(
        OUTPUT_DIR / "overall_metrics.csv",
        index=False,
        encoding="utf-8-sig",
    )

    print("\nOverall metrics:")
    print(Overall_metrics.to_string(index=False))

    # Product event metrics
    event_metrics = analyze_event_metrics(posts)

    event_metrics.to_csv(
        OUTPUT_DIR / "event_metics.csv",
        index=False,
        encoding="utf-8-sig",
    )

    print("\nEvent metrics:")
    print(event_metrics.to_string(index=False))

    print(f"\nResults saved to: {OUTPUT_DIR}")



if __name__ == "__main__":
    main()
