import yt_dlp
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class YouTubeService:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def download_video(self, url: str, video_id: str) -> Optional[str]:
        """YouTubeビデオをダウンロード"""
        try:
            output_path = self.output_dir / f"{video_id}.mp4"

            if output_path.exists():
                logger.info(f"Video already exists: {output_path}")
                return str(output_path)

            ydl_opts = {
                "format": "best[ext=mp4]",
                "outtmpl": str(self.output_dir / f"{video_id}"),
                "quiet": False,
                "no_warnings": False,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"Downloading: {url}")
                ydl.download([url])

            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to download video: {str(e)}")
            return None

    async def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """ビデオ情報を取得"""
        try:
            ydl_opts = {"quiet": True, "no_warnings": True}

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    "title": info.get("title"),
                    "description": info.get("description"),
                    "duration": info.get("duration"),
                    "thumbnail": info.get("thumbnail"),
                    "upload_date": info.get("upload_date"),
                }
        except Exception as e:
            logger.error(f"Failed to get video info: {str(e)}")
            return None
