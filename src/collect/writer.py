"""収集したツイートをCSVファイルに書く"""

from __future__ import annotations
import csv
from dataclasses import asdict

from src.utils.config import RAW_DATA_DIR
from .models import Tweet

class CSVWriter:
    
    def __init__(self) -> None:
        self.output_dir = RAW_DATA_DIR
        self.output_dir.mkdir(
            parents = True,
            exist_ok = True,
        )
        

    # 機能が被っていたのでまとめて扱いやすくした
    def write(
        self,
        filename: str,
        tweets: list[Tweet],
    ) -> None:
        
        csv_path = self.output_dir / filename

        file_exists = csv_path.exists()

        # 空リストが返ることがあるので一応
        if not tweets:
            return
        
        fieldnames = asdict(tweets[0]).keys()

        with csv_path.open(
            "a",
            newline="",
            encoding="utf-8",
        ) as f:
            
            writer = csv.DictWriter(
                f,
                fieldnames = fieldnames,
            )

            if not file_exists:
                writer.writeheader()

            for tweet in tweets:
                writer.writerow(asdict(tweet))