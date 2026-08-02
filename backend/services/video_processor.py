import cv2
import logging
from pathlib import Path
from typing import List
import base64
from io import BytesIO
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


class VideoProcessor:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def extract_key_frames(
        self, video_path: str, num_screenshots: int = 5
    ) -> List[str]:
        """重要なシーンを自動検出してスクリーンショット抽出"""
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

            # フレーム間の色差を計算して重要なシーンを検出
            scene_scores = []
            prev_frame = None

            # サンプリング: 毎秒1フレーム程度
            sample_interval = max(1, int(fps) if fps > 0 else 30)

            frame_idx = 0
            while frame_idx < total_frames:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()

                if not ret:
                    frame_idx += sample_interval
                    continue

                # グレースケール化してフレーム差を計算
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                if prev_frame is not None:
                    diff = cv2.absdiff(prev_frame, gray)
                    score = np.mean(diff)
                    scene_scores.append((frame_idx, score))

                prev_frame = gray
                frame_idx += sample_interval

            cap.release()

            # スコアが高いフレーム（シーン変化が大きい）を選択
            if scene_scores:
                # スコアの高い順にソート
                sorted_scenes = sorted(scene_scores, key=lambda x: x[1], reverse=True)
                # 上位のフレームを選択
                selected_frames = sorted([frame for frame, _ in sorted_scenes[:num_screenshots]])
            else:
                # フォールバック: 均等分割
                selected_frames = [
                    int((i + 1) * total_frames / (num_screenshots + 1))
                    for i in range(num_screenshots)
                ]

            logger.info(f"Selected key frames at: {selected_frames}")

            # 選定されたフレームを抽出
            cap = cv2.VideoCapture(video_path)
            for frame_num in selected_frames:
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
            logger.info(f"Extracted {len(screenshots)} key frame screenshots")
            return screenshots

        except Exception as e:
            logger.error(f"Failed to extract key frames: {str(e)}")
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
