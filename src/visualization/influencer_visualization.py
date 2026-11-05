""" Visualize user-level influencer metrics."""

import matplotlib.pyplot as plt
import pandas as pd

from src.utils.config import RESULT_DIR
from scipy.stats import spearmanr




INPUT_FILE = RESULT_DIR / "influencer" / "user_metrics.csv"
OUTPUT_DIR = RESULT_DIR / "visualization"


def load_user_metrics() -> pd.DataFrame:
    """ Load user-level engagement metrics. """
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"File not found: {INPUT_FILE}")

    return pd.read_csv(INPUT_FILE)


def plot_post_count_vs_likes(users: pd.DataFrame) -> None:
    """ Plot the relationship between post count and average likes."""
    single_post_users = users[users["post_count"] == 1]
    active_users = users[users["post_count"] >= 2]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.scatter(
        single_post_users["post_count"],
        single_post_users["avg_likes"],
        alpha=0.3,
        s=20,
        label="1 post",
    )

    ax.scatter(
        active_users["post_count"],
        active_users["avg_likes"],
        alpha=0.7,
        s=30,
        label="2<= posts",
    )

    ax.set_yscale("symlog", linthresh=1)

    ax.set_title("Post Count vs Average Likes")
    ax.set_xlabel("Number of Posts")
    ax.set_ylabel("Average Likes (symlog scale)")

    ax.legend()
    ax.grid(True, alpha=0.3)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "post_count_vs_likes.png"

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.show()

    print(f"Saved visualization: {output_path}")

def plot_post_count_vs_median_likes(users: pd.DataFrame) -> None:
    """ Plot the relationship between post count and median likes. """
    single_post_users = users[users["post_count"] == 1]
    active_users = users[users["post_count"] >= 2]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.scatter(
        single_post_users["post_count"],
        single_post_users["median_likes"],
        alpha=0.3,
        s=20,
        label="1 post",
    )

    ax.scatter(
        active_users["post_count"],
        active_users["median_likes"],
        alpha=0.7,
        s=30,
        label="2<= posts",
    )

    ax.set_yscale("symlog", linthresh=1)

    ax.set_title("Post Count vs Median Likes")
    ax.set_xlabel("Number of Posts")
    ax.set_ylabel("Median Likes (symlog scale)")

    ax.legend()
    ax.grid(True, alpha=0.3)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "post_count_vs_median_likes.png"

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.show()

    print(f"Saved visualization: {output_path}")

def analyze_post_count_correlation(users: pd.DataFrame) -> None:
    # 投稿数・いいね数ともに偏った分布と判明（先のvisualizationの実施）したのでfirstにSpearmanを用いる
    """ Analyze correlations between post count and engagement metrics. """

    metrics = ["avg_likes", "median_likes", "avg_retweets"]

    print("\nSpearman correlation analysis:")

    for metric in metrics:
        correlation, p_value = spearmanr(
            users["post_count"],
            users[metric],
        )

        print(f"\npost_count vs {metric}")
        print(f"Spearman correlation: {correlation:.4f}")
        print(f"p-value: {p_value:.6f}")

def plot_avg_likes_vs_retweets(users: pd.DataFrame) -> None:
    # いいね数とリポスト数の関係性、second
    """ Plot the relationship between average likes and retweets. """

    single_post_users = users[users["post_count"] == 1]
    active_users = users[users["post_count"] >= 2]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.scatter(
        single_post_users["avg_likes"],
        single_post_users["avg_retweets"],
        alpha=0.3,
        s=20,
        label="1 post",
    )

    ax.scatter(
        active_users["avg_likes"],
        active_users["avg_retweets"],
        alpha=0.7,
        s=30,
        label="2<= posts",
    )

    ax.set_xscale("symlog", linthresh=1)
    ax.set_yscale("symlog", linthresh=1)

    ax.set_title("Average Likes vs Average Retweets")
    ax.set_xlabel("Average Likes (symlog scale)")
    ax.set_ylabel("Average Retweets (symlog scale)")

    ax.legend()
    ax.grid(True, alpha=0.3)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "avg_likes_vs_retweets.png"

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.show()

    print(f"Saved visualization: {output_path}")

def analyze_engagement_correlation(users: pd.DataFrame) -> None:
    # 相関係数の算出、third
    """ Analyze correlation between likes and retweets."""

    correlation, p_value = spearmanr(
        users["avg_likes"],
        users["avg_retweets"],
    )

    print("\nEngagement correlation analysis:")
    print("avg_likes vs avg_retweets")
    print(f"Spearman correlation: {correlation:.4f}")
    print(f"p-value: {p_value:.6g}")

def analyze_median_engagement_correlation(users: pd.DataFrame) -> None:
    # 中央値を用いたいいね数とリポスト数の関係
    """ Analyze the correlation between median likes and retweets."""

    correlation, p_value = spearmanr(
        users["median_likes"],
        users["median_retweets"],
    )

    print("\nMedian engagement correlation analysis:")
    print("median_likes vs median_retweets")
    print(f"Spearman correlation: {correlation:.4f}")
    print(f"p-value: {p_value:.6g}")





def main() -> None:
    """ Run influencer visualization."""
    users = load_user_metrics()

    #plot_post_count_vs_likes(users)
    #plot_post_count_vs_median_likes(users)

    #analyze_post_count_correlation(users)

    #plot_avg_likes_vs_retweets(users)
    #analyze_engagement_correlation(users)

    analyze_median_engagement_correlation(users)


if __name__ == "__main__":
    main()