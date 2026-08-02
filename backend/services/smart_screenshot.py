"""
高度なスクリーンショット抽出
- トランスクリプト + シーン検出の組み合わせ
- 話題変化の時点でキャプチャ
"""

import cv2
import logging
from pathlib import Path
from typing import List, Optional
import base64
from io import BytesIO
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


class SmartScreenshot:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def extract_by_transcript(
        self,
        video_path: str,
        transcript_segments: list,
        num_screenshots: int = 5,
    ) -> List[str]:
        """
        トランスクリプトセグメントに基づいて重要なフレームを抽出

        話題が大きく変わった箇所でキャプチャ
        """
        screenshots = []

        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"Failed to open video: {video_path}")
                return []

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)

            if fps == 0:
                logger.warning("Invalid FPS")
                return []

            # セグメントの開始時間でスコア計算
            segment_scores = []

            if transcript_segments:
                for i, segment in enumerate(transcript_segments):
                    start_time = segment.get("start", 0)
                    text = segment.get("text", "").strip()

                    # 最小文字数でフィルタリング（無意味なセグメント除外）
                    if len(text) < 10:
                        continue

                    # セグメント間の距離スコア（話題の重要度の代理）
                    if i > 0:
                        prev_text = transcript_segments[i - 1].get("text", "")
                        # テキストの類似度（異なる = 話題変化 = 重要）
                        similarity = self._text_similarity(prev_text, text)
                        score = 1.0 - similarity  # 異なるほどスコア高い
                    else:
                        score = 1.0  # 最初のセグメント

                    frame_idx = int(start_time * fps)
                    segment_scores.append((frame_idx, score, text))

                logger.info(
                    f"Found {len(segment_scores)} segments with score variation"
                )

                # スコアが高いセグメント（話題変化が大きい）を選択
                if segment_scores:
                    sorted_segments = sorted(
                        segment_scores, key=lambda x: x[1], reverse=True
                    )
                    selected_frames = sorted(
                        [frame for frame, _, _ in sorted_segments[:num_screenshots]]
                    )
                else:
                    selected_frames = []
            else:
                logger.warning("No transcript segments provided")
                selected_frames = []

            # フォールバック：セグメントがない、またはスコアが足りない場合
            if len(selected_frames) < num_screenshots:
                logger.info("Using scene detection as fallback")
                fallback_frames = await self._extract_by_scene_change(
                    video_path, num_screenshots - len(selected_frames)
                )
                selected_frames.extend(fallback_frames)
                selected_frames = sorted(list(set(selected_frames)))[:num_screenshots]

            logger.info(f"Selected frames at: {selected_frames}")

            # フレームを抽出
            for frame_idx in selected_frames:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
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

    async def _extract_by_scene_change(
        self, video_path: str, num_screenshots: int
    ) -> List[int]:
        """シーン変化に基づいてフレーム取得（フォールバック）"""
        try:
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)

            scene_scores = []
            prev_frame = None
            sample_interval = max(1, int(fps) if fps > 0 else 30)

            frame_idx = 0
            while frame_idx < total_frames:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()

                if not ret:
                    frame_idx += sample_interval
                    continue

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                if prev_frame is not None:
                    diff = cv2.absdiff(prev_frame, gray)
                    score = np.mean(diff)
                    scene_scores.append((frame_idx, score))

                prev_frame = gray
                frame_idx += sample_interval

            cap.release()

            if scene_scores:
                sorted_scenes = sorted(
                    scene_scores, key=lambda x: x[1], reverse=True
                )
                selected = sorted(
                    [frame for frame, _ in sorted_scenes[:num_screenshots]]
                )
                return selected

            return []

        except Exception as e:
            logger.error(f"Scene detection failed: {str(e)}")
            return []

    @staticmethod
    def _text_similarity(text1: str, text2: str) -> float:
        """
        簡単なテキスト類似度計算
        共通単語の割合で判定
        """
        if not text1 or not text2:
            return 0.0

        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        # ジャッカード類似度
        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0
