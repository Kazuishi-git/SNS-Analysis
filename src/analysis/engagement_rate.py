""" Calculate engagement rates using follower counts."""

import pandas as pd

from src.utils.config import RAW_DATA_DIR, RESULT_DIR


OUTPUT_DIR = RESULT_DIR / "influencer"


def load_posts() -> pd.DataFrame:

    """ Load and combine all post CSV files."""
    csv_files = sorted(RAW_DATA_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError("No post CSV files found.")

    dataframes = [pd.read_csv(file) for file in csv_files]

    posts = pd.concat(dataframes, ignore_index=True)

    # Remove duplicated posts if they exist.
    posts = posts.drop_duplicates(subset="tweet_id")

    return posts


def load_users() -> pd.DataFrame:

    """ Load user information."""
    user_file = RAW_DATA_DIR / "users" / "users.csv"

    if not user_file.exists():
        raise FileNotFoundError("users.csv not found.")

    users = pd.read_csv(user_file)

    # Ensure each user appears only once.
    users = users.drop_duplicates(subset="author_id")

    return users


def merge_posts_and_users(
    posts: pd.DataFrame,
    users: pd.DataFrame,
    ) -> pd.DataFrame:

    """ Merge post data with follower counts."""
    merged = posts.merge(
        users[["author_id", "followers_count"]],
        on="author_id",
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    return merged

def calculate_post_er(posts: pd.DataFrame) -> pd.DataFrame:
    """ Calculate engagement rate for each post. """
    result = posts.copy()

    engagement_columns = ["likes", "retweets", "replies", "quotes"]

    result["engagement_count"] = result[engagement_columns].sum(
        axis=1,
        min_count=len(engagement_columns),
    )

    # フォロワー数が０または欠損している投稿はengagement_rateを計算しない
    valid_followers = (
        result["followers_count"].notna() & (result["followers_count"] > 0)
    )

    result["er"] = float("nan")

    result.loc[valid_followers, "er"] = (
        result.loc[valid_followers, "engagement_count"] 
        / result.loc[valid_followers, "followers_count"]
        * 100
    )

    return result

def aggregate_user_er(posts: pd.DataFrame) -> pd.DataFrame:
    """ Aggregate engagement metrics by user."""
    valid_posts = posts.dropna(subset=["er"])

    user_summary = (
        valid_posts
        .groupby("author_id")
        .agg(
            followers_count=("followers_count", "first"),
            post_count=("tweet_id", "count"),
            avg_er=("er", "mean"),
            median_er=("er", "median"),
            avg_likes=("likes", "mean"),
            median_likes=("likes", "median"),
            avg_retweets=("retweets", "mean"),
            median_retweets=("retweets", "median"),
            total_engagement=("engagement_count", "sum"),
        )
        .reset_index()
    )

    return user_summary


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    posts = load_posts()
    users = load_users()

    merged = merge_posts_and_users(posts, users)

    # 投稿単位のEngagementRateを計算
    post_er = calculate_post_er(merged)

    # ユーザ単位に集計
    user_er = aggregate_user_er(post_er)

    #結果の保存　
    post_er.to_csv(
        OUTPUT_DIR / "post_engagement_rate.csv",
        index=False,
        encoding="utf-8-sig",
    )

    user_er.to_csv(
        OUTPUT_DIR / "user_engagement_rate.csv",
        index=False,
        encoding="utf-8-sig",
    )

    matched = merged["_merge"] == "both"
    valid_followers = merged["followers_count"].notna()

    print(f"Total posts: {len(posts)}")
    print(f"Posts with valid ER: {post_er['er'].notna().sum()}")
    print(f"Users with valid ER: {user_er['author_id'].nunique()}")
    print(f"Average ER: {post_er['er'].mean():.4f}%")
    print(f"Median ER: {post_er['er'].median():.4f}%")



if __name__ == "__main__":
    main()