import whisper
import logging
from typing import Optional
import json

logger = logging.getLogger(__name__)


class TranscriptService:
    def __init__(self):
        self.model = None

    async def get_transcript(self, video_path: str) -> Optional[str]:
        """Whisperを使用してトランスクリプトを生成"""
        try:
            if self.model is None:
                logger.info("Loading Whisper model...")
                self.model = whisper.load_model("base")

            logger.info(f"Transcribing: {video_path}")
            result = self.model.transcribe(
                video_path, language="ja", fp16=False, verbose=False
            )

            transcript = result.get("text", "")
            logger.info(f"Transcription complete: {len(transcript)} chars")
            return transcript

        except Exception as e:
            logger.error(f"Failed to get transcript: {str(e)}")
            return None

    async def get_transcript_segments(self, video_path: str) -> Optional[list]:
        """セグメント付きトランスクリプトを取得"""
        try:
            if self.model is None:
                logger.info("Loading Whisper model...")
                self.model = whisper.load_model("base")

            logger.info(f"Transcribing with segments: {video_path}")
            result = self.model.transcribe(
                video_path, language="ja", fp16=False, verbose=False
            )

            segments = []
            for segment in result.get("segments", []):
                segments.append(
                    {
                        "start": segment.get("start"),
                        "end": segment.get("end"),
                        "text": segment.get("text"),
                    }
                )

            logger.info(f"Extracted {len(segments)} segments")
            return segments

        except Exception as e:
            logger.error(f"Failed to get transcript segments: {str(e)}")
            return None
