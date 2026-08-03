import yt_dlp
from pathlib import Path
from typing import Optional, Dict, Any
import logging
import re

logger = logging.getLogger(__name__)


class YouTubeService:
    def __init__(self, output_dir: Path, cookie_file: Optional[Path] = None):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cookie_file = cookie_file

    async def download_video(self, url: str, video_id: str) -> Optional[str]:
        """YouTubeビデオをダウンロード"""
        try:
            # 既存ファイルを確認（mp4、mkv、webmなど）
            existing_files = list(self.output_dir.glob(f"{video_id}.*"))
            if existing_files:
                video_file = existing_files[0]
                logger.info(f"Video already exists: {video_file}")
                return str(video_file)

            ydl_opts = {
                "format": "best",
                "outtmpl": str(self.output_dir / f"{video_id}.%(ext)s"),
                "quiet": False,
                "no_warnings": False,
                "postprocessors": [{
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4",
                }],
            }

            if self.cookie_file and self.cookie_file.exists():
                ydl_opts["cookiefile"] = str(self.cookie_file)
                logger.info(f"Using cookies from: {self.cookie_file}")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"Downloading: {url}")
                ydl.download([url])

            # ダウンロード後のファイルを検索
            downloaded_files = list(self.output_dir.glob(f"{video_id}.*"))
            if downloaded_files:
                return str(downloaded_files[0])

            logger.error("Downloaded file not found after yt-dlp completion")
            return None

        except Exception as e:
            logger.error(f"Failed to download video: {str(e)}")
            return None

    async def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """ビデオ情報を取得"""
        try:
            ydl_opts = {"quiet": True, "no_warnings": True}

            if self.cookie_file and self.cookie_file.exists():
                ydl_opts["cookiefile"] = str(self.cookie_file)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    "id": info.get("id"),
                    "title": info.get("title"),
                    "description": info.get("description"),
                    "duration": info.get("duration"),
                    "thumbnail": info.get("thumbnail"),
                    "upload_date": info.get("upload_date"),
                }
        except Exception as e:
            logger.error(f"Failed to get video info: {str(e)}")
            return None

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """URLからYouTubeビデオIDを抽出"""
        match = re.search(r"(?:v=|/shorts/|youtu\.be/)([A-Za-z0-9_-]{11})", url)
        return match.group(1) if match else None
