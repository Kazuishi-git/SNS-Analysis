# 取得されなかったユーザを調べる
""" Check missing user information."""

import csv
from pathlib import Path

from src.utils.config import RAW_DATA_DIR


def load_post_user_ids() -> set[str]:
    """ Load unique author IDs from post CSV files."""
    user_ids = set()

    for csv_file in RAW_DATA_DIR.glob("*.csv"):
        with csv_file.open(
            "r",
            newline="",
            encoding="utf-8",
        ) as f:
            reader = csv.DictReader(f)

            for row in reader:
                author_id = row.get("author_id")
                if author_id:
                    user_ids.add(author_id)

    return user_ids


def load_saved_users() -> tuple[set[str], int]:
    """ Load saved user IDs and count CSV rows."""
    csv_path = RAW_DATA_DIR / "users" / "users.csv"

    user_ids = set()
    row_count = 0

    with csv_path.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as f:
        reader = csv.DictReader(f)

        for row in reader:
            author_id = row.get("author_id")
            if author_id:
                user_ids.add(author_id)
                row_count += 1

    return user_ids, row_count


def main() -> None:
    post_user_ids = load_post_user_ids()
    saved_user_ids, row_count = load_saved_users()

    missing_ids = post_user_ids - saved_user_ids

    print(f"Post users: {len(post_user_ids)}")
    print(f"Saved users: {len(saved_user_ids)}")
    print(f"CSV rows: {row_count}")
    print(f"Missing users: {len(missing_ids)}")

    if missing_ids:
        print("\nMissing user IDs:")
        for user_id in sorted(missing_ids):
            print(user_id)


if __name__ == "__main__":
    main()
