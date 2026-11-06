import csv
import pandas as pd
from pathlib import Path
from collections import Counter

def merge_csv_files(csv_paths: list[Path]) -> pd.DataFrame:
    """複数のCSVファイルを統合する"""

    dataframes = []

    for path in csv_paths:
        df = pd.read_csv(path, encoding="utf-8")
        dataframes.append(df)

    merged_df = pd.concat(dataframes, ignore_index=True)

    return merged_df


def analyze_posts(df: pd.DataFrame) -> None:
    """統合した投稿データの基本情報を集計する"""

    print("=== Post Analysis ===")

    # 統合前の投稿数
    print(f"Total rows: {len(df)}")

    # 重複投稿の確認
    duplicate_count = df["tweet_id"].duplicated().sum()
    print(f"Duplicate posts: {duplicate_count}")

    # 重複投稿の除去
    df = df.drop_duplicates(subset="tweet_id")

    # 投稿数
    print(f"Unique posts: {len(df)}")

    # ユーザー数
    if "author_id" in df.columns:
        print(f"Unique users: {df['author_id'].nunique()}")

    # ユーザー別投稿数
    if "author_id" in df.columns:
        user_post_counts = df["author_id"].value_counts()

        print("\n=== User Post Counts ===")
        print(user_post_counts.describe())

    return df


def main():

    # CSVファイルのパス（自分で設定）
    csv_paths = [
        Path("data/raw/starbucks_new_20260828.csv"),
        Path("data/raw/starbucks_new_20260829.csv"),
        Path("data/raw/starbucks_new_20260830.csv"),
        Path("data/raw/starbucks_new_20260831.csv"),
        Path("data/raw/starbucks_new_20260901.csv"),
        Path("data/raw/starbucks_new_20260902.csv"),
        Path("data/raw/starbucks_new_20260903.csv"),
        Path("data/raw/starbucks_new_20260904.csv"),
        Path("data/raw/starbucks_new_20260905.csv"),
        Path("data/raw/starbucks_new_20260906.csv"),
        Path("data/raw/starbucks_new_20260907.csv"),
    ]

    # CSV統合
    merged_df = merge_csv_files(csv_paths)

    # 集計
    merged_df = analyze_posts(merged_df)


if __name__ == "__main__":
    main()