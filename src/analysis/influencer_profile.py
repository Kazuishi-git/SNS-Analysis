""" Analyze post and user-level engagement metrics."""

from pathlib import Path
import pandas as pd
from src.utils.config import DATA_DIR, RESULT_DIR


RAW_DATA_DIR = DATA_DIR / "raw"
OUTPUT_DIR = RESULT_DIR / "influencer"


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

    print(f"Total posts: {len(posts)}")
    print(f"Unique users: {posts['author_id'].nunique()}")
    print("\nPost-level metrics:")
    print(post_metrics.to_string())

    print("\nTop 10 users by average likes:")
    print(user_metrics.head(10).to_string(index=False))

    # 投稿数別のユーザー数
    print("\nUsers by post count:")
    print(
        user_metrics["post_count"]
        .value_counts()
        .sort_index()
        .head(10)
    )

    # 2件以上投稿したユーザー
    active_users = user_metrics[
        user_metrics["post_count"] >= 2
    ].copy()

    print(f"\nUsers with 2 or more posts: {len(active_users)}")

    print("\nTop 10 active users by average likes:")
    print(
        active_users
        .sort_values("avg_likes", ascending=False)
        .head(10)
        .to_string(index=False)
    )

    print(f"\nResults saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
