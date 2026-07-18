# 収集したツイートをCSVファイルに書く

from pathlib import Path

from src.utils.config import DATA_DIR
from .models import Tweet

class CSVWriter:
    
    def __init__(self) -> None:
        self.output_dir = DATA_DIR
        
    def write_header(
        self,
        filename: str,
    ) -> None:
        pass
    
    def write_rows(
        self,
        filename: str,
        tweets: list[Tweet],
    ) -> None:
        pass
    