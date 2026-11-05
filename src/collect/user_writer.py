""" 収集したユーザ情報をCSVファイルに書く"""

from __future__ import annotations

import csv
from dataclasses import asdict

from src.utils.config import RAW_DATA_DIR
from .models import User


class UserCSVWriter :
    def __init__(self) -> None:
        self.output_dir = RAW_DATA_DIR / "users"
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )
        self.filename = "users.csv"
        self.csv_path = self.output_dir / self.filename
        self._known_user_ids : set[str] | None = None

    def get_existing_user_ids(self) -> set[str]:
        """ Load IDs of users already saved in the CSV."""
        if self._known_user_ids is None:
            self._known_user_ids = set()

            if self.csv_path.exists():
                with self.csv_path.open(
                    "r",
                    newline="",
                    encoding="utf-8",
                ) as f:
                    reader = csv.DictReader(f)

                    for row in reader:
                        author_id = row.get("author_id")
                        if author_id:
                            self._known_user_ids.add(author_id)

        return self._known_user_ids

    def write(self, users: list[User]) -> None:
        """ Append new user information to the CSV."""
        if not users:
            return

        known_ids = self.get_existing_user_ids()

        new_users = []
        for user in users:
            author_id = str(user.author_id)

            if author_id in known_ids:
                continue

            new_users.append(user)
            known_ids.add(author_id)

        if not new_users:
            return

        file_exists = (
            self.csv_path.exists()
            and self.csv_path.stat().st_size > 0
        )

        fieldnames = list(asdict(new_users[0]).keys())

        with self.csv_path.open(
            "a",
            newline="",
            encoding="utf-8",
        ) as f:
            writer = csv.DictWriter(
                f,
                fieldnames=fieldnames,
            )

            if not file_exists:
                writer.writeheader()

            for user in new_users:
                writer.writerow(asdict(user))