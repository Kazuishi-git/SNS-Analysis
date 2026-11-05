from src.collect.user_collector import XUserCollector


def main() -> None:
    """Test X API user collection with a small batch."""

    collector = XUserCollector()

    print("Starting user collection test.")

    # 投稿CSVに含まれる全ユーザを対象に、また既存ユーザは自動的に除外
    collector.collect()

    print("User collection test completed.")

    existing_ids = collector.writer.get_existing_user_ids()

    print(f"Saved users: {len(existing_ids)}")


if __name__ == "__main__":
    main()
