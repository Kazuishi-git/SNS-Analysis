""" X APIからユーザー情報を収集する """

import csv
from datetime import datetime, UTC

from tweepy import Response
from tweepy.errors import TweepyException

from .client import XClient
from .models import User
from .user_writer import UserCSVWriter

from src.utils.config import RAW_DATA_DIR
from src.utils.logger import logger


class XUserCollector:
    """ Manage the user information collection workflow. """

    BATCH_SIZE = 100

    def __init__(self) -> None:
        self.client = XClient()
        self.writer = UserCSVWriter()

    def collect(self) -> None:
        """ Collect user information for all authors in post CSV files."""
        user_ids = self._load_user_ids()
        new_user_ids = self._get_new_user_ids(user_ids)

        logger.info(
            "Found %d unique users. %d new users to collect.",
            len(user_ids),
            len(new_user_ids),
        )

        if not new_user_ids:
            logger.info("No new users to collect.")
            return

        self._collect_users(new_user_ids)

        logger.info("User collection finished.")

    def _load_user_ids(self) -> list[str]:
        """ Load unique author IDs from post CSV files."""
        user_ids: set[str] = set()

        csv_files = sorted(RAW_DATA_DIR.glob("*.csv"))

        if not csv_files:
            raise FileNotFoundError(
                "No post CSV files found in data/raw."
            )

        for csv_file in csv_files:
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

        return sorted(user_ids)

    def _get_new_user_ids(
        self,
        user_ids: list[str],
    ) -> list[str]:
        
        """ Exclude users whose information has already been saved."""
        # 再実行時、未取得ユーザのみを対象とする
        existing_ids = self.writer.get_existing_user_ids()

        return [
            user_id
            for user_id in user_ids
            if user_id not in existing_ids
        ]

    def _collect_users(self, user_ids: list[str]) -> None:
        """ Collect user information in batches of up to 100 IDs."""
        total = len(user_ids)

        for start in range(0, total, self.BATCH_SIZE):
            batch = user_ids[start:start + self.BATCH_SIZE]

            try:
                response = self.client.get_users(batch)
                users = self._convert_response(response)

                # 取得したユーザ情報は即時保存
                self.writer.write(users)

                logger.info(
                    "Collected %d / %d users.",
                    min(start + len(batch), total),
                    total,
                )

            except TweepyException:
                logger.exception(
                    "Failed to collect users. Batch starts at %d.",
                    start,
                )
                raise

    def _convert_response(
        self,
        response: Response,
    ) -> list[User]:
        """ Convert an X API response into User objects."""
        users: list[User] = []

        if response.data is None:
            logger.warning("No user data returned from X API.")
            return users

        retrieved_at = datetime.now(UTC)

        for user in response.data:
            metrics = user.public_metrics

            if metrics is None:
                logger.warning(
                    "Public metrics unavailable for user: %s",
                    user.id,
                )
                continue

            users.append(
                User(
                    author_id=str(user.id),
                    followers_count=metrics["followers_count"],
                    following_count=metrics["following_count"],
                    tweet_count=metrics["tweet_count"],
                    listed_count=metrics["listed_count"],
                    retrieved_at=retrieved_at,
                )
            )

        return users
