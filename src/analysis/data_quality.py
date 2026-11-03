""" Validate the quality of collected X post datasets."""

import pandas as pd

from src.utils.config import RAW_DATA_DIR


REQUIRED_COLUMNS = [
    "event_id",
    "tweet_id",
    "author_id",
    "created_at",
    "retrieved_at",
    "text",
    "likes",
    "retweets",
    "replies",
    "quotes",
]

NUMERIC_COLUMNS = [
    "likes",
    "retweets",
    "replies",
    "quotes",
]

def check_csv(filename):
    """ Check the quality of one CSV file. """

    filepath = RAW_DATA_DIR / filename
    df = pd.read_csv(filepath)

    print("\n" + "=" * 60)
    print(f"File: {filename}")
    print("=" * 60)

    # 1. 投稿件数
    print(f"投稿件数: {len(df)}")

    # 2. コラムの確認
    missing_columns = [
        col for col in REQUIRED_COLUMNS if col not in df.columns
    ]

    if missing_columns:
        print(f"不足カラム: {missing_columns}")
        return df

    # 3. 重複投稿
    print(f"tweet_id重複数: {df['tweet_id'].duplicated().sum()}")

    # 4. 欠損値
    print("\n【欠損値】")
    print(df[REQUIRED_COLUMNS].isnull().sum())

    # 5. 投稿日時
    created_at = pd.to_datetime(
        df["created_at"], utc=True, errors="coerce"
    )

    created_at_jst = created_at.dt.tz_convert("Asia/Tokyo")

    print("\n【投稿日時：日本時間】")
    print(f"最古: {created_at_jst.min()}")
    print(f"最新: {created_at_jst.max()}")

    print(f"日時変換失敗数: {created_at.isna().sum()}")

    # 6. 数値データの基本統計量
    print("\n【投稿反応の統計量】")

    for col in NUMERIC_COLUMNS:
        values = pd.to_numeric(df[col], errors="coerce")
        print(f"\n{col}")
        print(values.describe())

    return df


def main():
    """ Check all collected daily CSV files. """

    csv_files = sorted(RAW_DATA_DIR.glob("*.csv"))

    if not csv_files:
        print("CSVファイルが見つかりません。")
        return

    all_data = []

    for filepath in csv_files:
        df = check_csv(filepath.name)
        all_data.append(df)

    # 全CSVを統合して重複を確認
    combined = pd.concat(all_data, ignore_index=True)

    print("\n" + "=" * 60)
    print("【全データの集計】")
    print("=" * 60)

    print(f"CSVファイル数: {len(csv_files)}")
    print(f"総投稿件数: {len(combined)}")
    print(
        "全ファイル間のtweet_id重複数: "
        f"{combined['tweet_id'].duplicated().sum()}"
    )


if __name__ == "__main__":
    main()