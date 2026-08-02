from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import logging
import uuid
from pathlib import Path

from services import (
    YouTubeService,
    VideoProcessor,
    TranscriptService,
    SummarizerService,
    ReportGenerator,
)
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["summarize"])

# サービスのインスタンス化
youtube_service = YouTubeService(settings.PROCESSING_DIR)
video_processor = VideoProcessor(settings.PROCESSING_DIR)
transcript_service = TranscriptService()
summarizer_service = SummarizerService()
report_generator = ReportGenerator()


class SummarizeRequest(BaseModel):
    url: str
    include_detailed_report: bool = False


class SummarizeResponse(BaseModel):
    video_id: str
    title: str
    description: str
    duration: float
    summary: str
    screenshots: list[str]
    detailed_report: Optional[str] = None


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_video(request: SummarizeRequest):
    """YouTubeビデオをサマライズ（JSON）"""
    try:
        # 生成ID
        video_id = str(uuid.uuid4())[:8]

        logger.info(f"Processing video: {request.url}")

        # ビデオ情報取得
        video_info = await youtube_service.get_video_info(request.url)
        if not video_info:
            raise HTTPException(status_code=400, detail="Failed to get video info")

        # ビデオダウンロード
        video_path = await youtube_service.download_video(request.url, video_id)
        if not video_path:
            raise HTTPException(status_code=400, detail="Failed to download video")

        # トランスクリプト取得
        transcript = await transcript_service.get_transcript(video_path)
        if not transcript:
            raise HTTPException(
                status_code=400, detail="Failed to get transcript"
            )

        # サマリー生成
        summary = await summarizer_service.summarize_transcript(transcript)
        if not summary:
            raise HTTPException(status_code=400, detail="Failed to summarize")

        # 重要なシーンからスクリーンショット抽出
        screenshots = await video_processor.extract_key_frames(
            video_path, num_screenshots=settings.SCREENSHOT_COUNT
        )

        # 詳細レポート（オプション）
        detailed_report = None
        if request.include_detailed_report:
            detailed_report = await summarizer_service.generate_detailed_report(
                title=video_info.get("title", ""),
                description=video_info.get("description", ""),
                transcript=transcript,
                duration=video_info.get("duration", 0),
            )

        return SummarizeResponse(
            video_id=video_id,
            title=video_info.get("title", ""),
            description=video_info.get("description", ""),
            duration=video_info.get("duration", 0),
            summary=summary,
            screenshots=screenshots,
            detailed_report=detailed_report,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize-html")
async def summarize_video_html(request: SummarizeRequest):
    """YouTubeビデオをサマライズしてHTML報告書として出力"""
    try:
        # 生成ID
        video_id = str(uuid.uuid4())[:8]

        logger.info(f"Processing video for HTML report: {request.url}")

        # ビデオ情報取得
        video_info = await youtube_service.get_video_info(request.url)
        if not video_info:
            raise HTTPException(status_code=400, detail="Failed to get video info")

        # ビデオダウンロード
        video_path = await youtube_service.download_video(request.url, video_id)
        if not video_path:
            raise HTTPException(status_code=400, detail="Failed to download video")

        # トランスクリプト取得
        transcript = await transcript_service.get_transcript(video_path)
        if not transcript:
            raise HTTPException(
                status_code=400, detail="Failed to get transcript"
            )

        # サマリー生成
        summary = await summarizer_service.summarize_transcript(transcript)
        if not summary:
            raise HTTPException(status_code=400, detail="Failed to summarize")

        # 重要なシーンからスクリーンショット抽出
        screenshots = await video_processor.extract_key_frames(
            video_path, num_screenshots=settings.SCREENSHOT_COUNT
        )

        # 詳細レポート（オプション）
        detailed_report = None
        if request.include_detailed_report:
            detailed_report = await summarizer_service.generate_detailed_report(
                title=video_info.get("title", ""),
                description=video_info.get("description", ""),
                transcript=transcript,
                duration=video_info.get("duration", 0),
            )

        # HTMLレポート生成
        html_content = report_generator.generate_html_report(
            title=video_info.get("title", ""),
            description=video_info.get("description", ""),
            duration=video_info.get("duration", 0),
            summary=summary,
            screenshots=screenshots,
            detailed_report=detailed_report,
        )

        return HTMLResponse(
            content=html_content,
            headers={
                "Content-Disposition": f"inline; filename=video-summary-{video_id}.html"
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating HTML report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "ok"}
