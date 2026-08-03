import whisper
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ハルシネーション（無音・ノイズ区間での意味不明な出力）を除外するための閾値
NO_SPEECH_PROB_THRESHOLD = 0.6
AVG_LOGPROB_THRESHOLD = -1.0


class TranscriptService:
    def __init__(self):
        self.model = None
        self.detected_language: Optional[str] = None

    def _load_model(self):
        if self.model is None:
            logger.info("Loading Whisper model...")
            self.model = whisper.load_model("base")

    def _transcribe(self, video_path: str, language: Optional[str] = None) -> dict:
        """
        Whisperで文字起こし

        language=None の場合は自動言語検出を使用する。
        言語を固定すると、音声と異なる言語の当てはめが発生し、
        意味不明な多言語混在テキスト（ハルシネーション）の原因になるため注意。
        """
        self._load_model()
        result = self.model.transcribe(
            video_path,
            language=language,
            fp16=False,
            verbose=False,
            condition_on_previous_text=False,
        )
        self.detected_language = result.get("language")
        logger.info(f"Detected language: {self.detected_language}")
        return result

    @staticmethod
    def _is_hallucinated(segment: dict) -> bool:
        """無音・ノイズ区間でのハルシネーション（意味不明な出力）を検出"""
        no_speech_prob = segment.get("no_speech_prob", 0) or 0
        avg_logprob = segment.get("avg_logprob", 0) or 0
        return no_speech_prob > NO_SPEECH_PROB_THRESHOLD or avg_logprob < AVG_LOGPROB_THRESHOLD

    async def get_transcript(
        self, video_path: str, language: Optional[str] = None
    ) -> Optional[str]:
        """Whisperを使用してトランスクリプトを生成"""
        try:
            logger.info(f"Transcribing: {video_path}")
            result = self._transcribe(video_path, language=language)

            segments = [
                seg for seg in result.get("segments", [])
                if not self._is_hallucinated(seg)
            ]
            transcript = "".join(seg.get("text", "") for seg in segments).strip()

            logger.info(f"Transcription complete: {len(transcript)} chars")
            return transcript

        except Exception as e:
            logger.error(f"Failed to get transcript: {str(e)}")
            return None

    async def get_transcript_segments(
        self, video_path: str, language: Optional[str] = None
    ) -> Optional[list]:
        """セグメント付きトランスクリプトを取得（時間情報付き）"""
        try:
            logger.info(f"Transcribing with segments: {video_path}")
            result = self._transcribe(video_path, language=language)

            segments = []
            removed = 0
            for segment in result.get("segments", []):
                if self._is_hallucinated(segment):
                    removed += 1
                    continue
                segments.append(
                    {
                        "start": segment.get("start"),
                        "end": segment.get("end"),
                        "text": segment.get("text"),
                        "id": segment.get("id"),
                    }
                )

            if removed:
                logger.info(f"Removed {removed} likely-hallucinated segments")
            logger.info(f"Extracted {len(segments)} segments")
            return segments

        except Exception as e:
            logger.error(f"Failed to get transcript segments: {str(e)}")
            return None

    async def filter_important_segments(self, segments: list, min_length: int = 15) -> list:
        """意味のあるセグメント（十分な長さ）をフィルタリング"""
        if not segments:
            return []

        filtered = [
            seg for seg in segments
            if len(seg.get("text", "").strip()) >= min_length
        ]

        logger.info(
            f"Filtered segments: {len(segments)} → {len(filtered)} "
            f"(removed short segments)"
        )
        return filtered
