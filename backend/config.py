from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # API キーは不要（Claude Code セッション内で処理）
    YOUTUBE_API_KEY: str = ""

    # ビデオ処理
    MAX_VIDEO_DURATION: int = 3600  # 秒
    SCREENSHOT_COUNT: int = 5
    SCREENSHOT_QUALITY: int = 85

    # サマライズ設定
    # 注: Claude が直接処理するため、APIキーなし
    SUMMARY_MODEL: str = "claude-3-5-sonnet-20241022"
    SUMMARY_MAX_TOKENS: int = 1000

    # ファイルパス
    UPLOAD_DIR: Path = Path(__file__).parent / "tmp" / "uploads"
    PROCESSING_DIR: Path = Path(__file__).parent / "tmp" / "processing"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
