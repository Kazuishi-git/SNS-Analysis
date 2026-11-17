"""収集したツイートをCSVファイルに書く"""

from __future__ import annotations
import csv
from dataclasses import asdict
from pathlib import Path

from src.utils.config import RAW_DATA_DIR
from .models import Tweet

class CSVWriter:

    # 指定がなければ、RAW_DATA_DIRを使う
    def __init__(self, output_dir: Path = RAW_DATA_DIR) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(
            parents = True,
            exist_ok = True
        )

        # ファイルごとに保存済みのtweet_idを管理する
        self._known_tweet_ids: dict[str, set[str]] = {}
        

    # 機能が被っていたのでまとめて扱いやすくした
    def write(
        self,
        filename: str,
        tweets: list[Tweet],
    ) -> None:

        # 空リストが返ることがあるので一応
        if not tweets:
            return

        csv_path = self.output_dir / filename

        # 初回だけ既存CSVのIDを読み込む
        if filename not in self._known_tweet_ids:
            self._known_tweet_ids[filename] = (
                self._load_existing_ids(filename)
            )

        known_ids = self._known_tweet_ids[filename]

        # 未保存の投稿だけを抽出
        new_tweets = []
        new_tweet_ids = set()

        # 重複を除外
        for tweet in tweets:
            tweet_id = str(tweet.tweet_id)

            if tweet_id in known_ids or tweet_id in new_tweet_ids:
                continue

            new_tweets.append(tweet)# 書き込み前にはIDを登録しない
            new_tweet_ids.add(tweet_id)

        # 全権が保存済みなら書き込まない
        if not new_tweets:
            return
        file_exists = csv_path.exists()
        csv_has_data = file_exists and csv_path.stat().st_size > 0


        fieldnames = list(asdict(new_tweets[0]).keys())

        # CSVへ書き込み
        with csv_path.open("a", newline="", encoding="utf-8",) as f:
            writer = csv.DictWriter(
                f,
                fieldnames = fieldnames
            )

            if not csv_has_data:
                writer.writeheader()

            for tweet in new_tweets:
                writer.writerow(asdict(tweet))

        # CSVへの書き込みが正常終了した後に保存済みIDとして登録する
        known_ids.update(new_tweet_ids)

    def _load_existing_ids(self, filename: str) -> set[str]:
                csv_path = self.output_dir / filename
                existing_ids: set[str] = set()
        
                if not csv_path.exists():
                    return existing_ids
        
                with csv_path.open("r", newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
        
                    for row in reader:
                        tweet_id = row.get("tweet_id")
                        if tweet_id:
                            existing_ids.add(tweet_id)
        
                return existing_ids