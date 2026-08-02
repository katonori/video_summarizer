import cv2
import logging
from pathlib import Path
from typing import List
import base64
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)


class VideoProcessor:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def extract_screenshots(
        self, video_path: str, num_screenshots: int = 5
    ) -> List[str]:
        """ビデオからスクリーンショットを抽出（base64エンコード）"""
        screenshots = []

        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"Failed to open video: {video_path}")
                return []

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames == 0:
                logger.error(f"No frames in video: {video_path}")
                return []

            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_indices = [
                int((i + 1) * total_frames / (num_screenshots + 1))
                for i in range(num_screenshots)
            ]

            for idx, frame_num in enumerate(frame_indices):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                ret, frame = cap.read()

                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    img.thumbnail((640, 360))

                    buffer = BytesIO()
                    img.save(buffer, format="JPEG", quality=85)
                    img_base64 = base64.b64encode(buffer.getvalue()).decode()
                    screenshots.append(f"data:image/jpeg;base64,{img_base64}")

            cap.release()
            logger.info(f"Extracted {len(screenshots)} screenshots")
            return screenshots

        except Exception as e:
            logger.error(f"Failed to extract screenshots: {str(e)}")
            return []

    async def get_video_duration(self, video_path: str) -> float:
        """ビデオの長さを取得（秒）"""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return 0.0

            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()

            return total_frames / fps if fps > 0 else 0.0
        except Exception as e:
            logger.error(f"Failed to get video duration: {str(e)}")
            return 0.0
