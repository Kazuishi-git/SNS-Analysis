from datetime import datetime, UTC

from src.collect.models import User
from src.collect.user_writer import UserCSVWriter


def main() -> None:
    # テスト
    """ Test user CSV writing and duplicate handling."""

    writer = UserCSVWriter()

    users = [
        User(
            author_id="test_user_001",
            followers_count=1000,
            following_count=500,
            tweet_count=3000,
            listed_count=10,
            retrieved_at=datetime.now(UTC),
        ),
        User(
            author_id="test_user_002",
            followers_count=2000,
            following_count=800,
            tweet_count=5000,
            listed_count=20,
            retrieved_at=datetime.now(UTC),
        ),
    ]

    writer.write(users)
    print("First write completed.")

    # 同じユーザーを再度書き込む
    writer.write(users)
    print("Second write completed.")

    existing_ids = writer.get_existing_user_ids()

    print("Existing user IDs:")
    print(existing_ids)


if __name__ == "__main__":
    main()
