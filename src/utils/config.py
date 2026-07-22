# project configuration

from pathlib import Path
from dotenv import load_dotenv
import os

# プロジェクトルート
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# .env を読み込む
load_dotenv(PROJECT_ROOT / ".env")

# API
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

" ディレクトリ"
DATA_DIR = PROJECT_ROOT / "data"

RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"

RESULT_DIR = PROJECT_ROOT / "result"
