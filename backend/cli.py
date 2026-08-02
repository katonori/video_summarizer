#!/usr/bin/env python3
"""
YouTube Video Summarizer CLI
シンプルなコマンドラインツール
"""

import asyncio
import argparse
import sys
from pathlib import Path
import logging

# ローカルインポート
from services import (
    YouTubeService,
    VideoProcessor,
    TranscriptService,
    SummarizerService,
    ReportGenerator,
    SmartScreenshot,
)
from config import settings

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    parser = argparse.ArgumentParser(
        description="YouTube Video Summarizer - CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python cli.py https://www.youtube.com/watch?v=...
  python cli.py https://www.youtube.com/watch?v=... --detailed
  python cli.py https://www.youtube.com/watch?v=... -o report.html
        """
    )

    parser.add_argument(
        "url",
        help="YouTubeビデオのURL"
    )
    parser.add_argument(
        "-o", "--output",
        help="出力ファイル名（デフォルト: report-{video_id}.html）",
        default=None
    )
    parser.add_argument(
        "-d", "--detailed",
        action="store_true",
        help="詳細レポートも生成する"
    )
    parser.add_argument(
        "--screenshots",
        type=int,
        default=settings.SCREENSHOT_COUNT,
        help=f"スクリーンショット数（デフォルト: {settings.SCREENSHOT_COUNT}）"
    )

    args = parser.parse_args()

    try:
        # 初期化
        youtube_service = YouTubeService(settings.PROCESSING_DIR)
        video_processor = VideoProcessor(settings.PROCESSING_DIR)
        transcript_service = TranscriptService()
        summarizer_service = SummarizerService()
        report_generator = ReportGenerator()
        smart_screenshot = SmartScreenshot(settings.PROCESSING_DIR)

        print("\n🎬 YouTube Video Summarizer")
        print("=" * 50)
        print(f"\n📥 ビデオ情報を取得中...\n")

        # ビデオ情報取得
        video_info = await youtube_service.get_video_info(args.url)
        if not video_info:
            raise Exception("ビデオ情報の取得に失敗しました")

        print(f"✅ タイトル: {video_info['title']}")
        print(f"✅ 長さ: {int(video_info['duration'])}秒\n")

        # ビデオダウンロード
        print("⏳ ビデオをダウンロード中...\n")
        video_path = await youtube_service.download_video(args.url, "temp_video")
        if not video_path:
            raise Exception("ビデオのダウンロードに失敗しました")

        print("✅ ダウンロード完了\n")

        # トランスクリプト生成
        print("⏳ トランスクリプトを生成中...\n")
        transcript = await transcript_service.get_transcript(video_path)
        if not transcript:
            raise Exception("トランスクリプトの生成に失敗しました")

        print(f"✅ トランスクリプト完了（{len(transcript)}文字）\n")

        # サマリー生成
        print("⏳ AIでサマライズ中...\n")
        summary = await summarizer_service.summarize_transcript(transcript)
        if not summary:
            raise Exception("サマリー生成に失敗しました")

        print("✅ サマリー完了\n")

        # スクリーンショット抽出（トランスクリプト + シーン検出）
        print(f"⏳ トランスクリプトベースのキーフレームを抽出中（{args.screenshots}枚）...\n")

        # トランスクリプトセグメント取得
        segments = await transcript_service.get_transcript_segments(video_path)
        if segments:
            # フィルタリング（意味のあるセグメントのみ）
            segments = await transcript_service.filter_important_segments(segments)
            print(f"   📝 {len(segments)}個の重要なセグメントを検出\n")

        # Smart Screenshot: トランスクリプト + シーン検出
        screenshots = await smart_screenshot.extract_by_transcript(
            video_path,
            segments=segments,
            num_screenshots=args.screenshots
        )
        print(f"✅ {len(screenshots)}枚のスクリーンショット抽出完了\n")

        # 詳細レポート（オプション）
        detailed_report = None
        if args.detailed:
            print("⏳ 詳細レポートを生成中...\n")
            detailed_report = await summarizer_service.generate_detailed_report(
                title=video_info.get("title", ""),
                description=video_info.get("description", ""),
                transcript=transcript,
                duration=video_info.get("duration", 0),
            )
            print("✅ 詳細レポート完了\n")

        # HTMLレポート生成
        print("📝 HTMLレポートを生成中...\n")
        html_content = report_generator.generate_html_report(
            title=video_info.get("title", ""),
            description=video_info.get("description", ""),
            duration=video_info.get("duration", 0),
            summary=summary,
            screenshots=screenshots,
            detailed_report=detailed_report,
        )

        # ファイルに保存
        output_file = args.output or f"report-{video_info['title'][:30]}.html"
        output_path = Path(output_file).absolute()
        output_path.write_text(html_content, encoding="utf-8")

        print(f"✅ HTMLレポート保存完了\n")
        print("=" * 50)
        print(f"\n📄 出力ファイル: {output_path}\n")
        print(f"✨ レポートを以下で確認できます:")
        print(f"   file://{output_path}\n")

    except KeyboardInterrupt:
        print("\n\n❌ キャンセルされました\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ エラー: {str(e)}\n")
        logger.exception("Exception occurred")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
