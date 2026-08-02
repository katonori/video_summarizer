#!/usr/bin/env python3
"""
Claude Code セッション内での実行用スクリプト

このスクリプトは Claude Code セッション内で実行され、
Claude が直接サマリー処理を行います。

外部 API (Anthropic API) へのアクセスは不要です。
"""

import asyncio
import sys
from pathlib import Path
import logging

# プロジェクトディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from services.youtube_service import YouTubeService
from services.transcript_service import TranscriptService
from services.video_processor import VideoProcessor
from services.report_generator import ReportGenerator
from services.claude_summarizer import ClaudeSummarizer
from config import settings

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    if len(sys.argv) < 2:
        print("""
╔════════════════════════════════════════════════════════════════╗
║         Claude Code 内でのYouTube Video Summarizer           ║
╚════════════════════════════════════════════════════════════════╝

使用方法:
  python summarize_in_claude.py <YouTube URL> [--detailed]

例:
  python summarize_in_claude.py "https://www.youtube.com/watch?v=..."
  python summarize_in_claude.py "https://www.youtube.com/watch?v=..." --detailed

特徴:
  ✓ Claude が直接処理 (API キー不要)
  ✓ Claude Code セッション内で実行
  ✓ ビデオダウンロード＆トランスクリプト＆サマリーを一度に実行

処理フロー:
  1. YouTubeビデオのメタデータ取得
  2. ビデオファイルをダウンロード
  3. Whisper でトランスクリプト生成
  4. 👈 Claude がサマリー処理を行う (API キー不要)
  5. スクリーンショット抽出
  6. HTML レポート生成
""")
        sys.exit(1)

    url = sys.argv[1]
    detailed_report = "--detailed" in sys.argv

    try:
        print("\n" + "=" * 60)
        print("🚀 Claude Code 内での処理を開始します")
        print("=" * 60)

        # 初期化
        youtube_service = YouTubeService(settings.PROCESSING_DIR)
        transcript_service = TranscriptService()
        video_processor = VideoProcessor(settings.PROCESSING_DIR)
        report_generator = ReportGenerator()
        claude_summarizer = ClaudeSummarizer()  # API キー不要

        print("\n📡 ステップ 1: ビデオ情報を取得")
        video_info = await youtube_service.get_video_info(url)
        if not video_info:
            raise Exception("ビデオ情報の取得に失敗しました")

        print(f"  ✅ タイトル: {video_info['title']}")
        print(f"  ✅ 長さ: {int(video_info['duration'])}秒")

        print("\n⬇️  ステップ 2: ビデオをダウンロード")
        video_path = await youtube_service.download_video(url, "claude_video")
        if not video_path:
            raise Exception("ビデオのダウンロードに失敗しました")
        print(f"  ✅ ダウンロード完了: {video_path}")

        print("\n🗣️  ステップ 3: トランスクリプトを生成 (Whisper)")
        transcript = await transcript_service.get_transcript(video_path)
        if not transcript:
            raise Exception("トランスクリプトの生成に失敗しました")
        print(f"  ✅ トランスクリプト完了: {len(transcript)}文字")

        print("\n" + "=" * 60)
        print("👉 ステップ 4: Claude によるサマリー処理")
        print("=" * 60)
        print("""
このステップから、Claude Code セッション内で Claude が
直接テキスト処理を行います。

【プロンプト】
以下のYouTubeビデオのトランスクリプトを、分かりやすく
日本語で要約してください。

【要約のポイント】
✓ 主なトピックを箇条書きで記載
✓ 重要な発見や結論をハイライト
✓ わかりやすく、簡潔に
✓ 適切なセクションに分ける

【トランスクリプト】
""")
        print(transcript[:500] + "...\n")

        # 👈 ここで Claude が処理を行う
        print("⏳ Claude がテキスト分析中...")
        summary = await claude_summarizer.summarize_transcript(transcript)

        if not summary:
            raise Exception("サマリー生成に失敗しました")

        print("\n✅ Claude によるサマリー完了")
        print("-" * 60)
        print(summary[:300] + "...\n")

        print("📸 ステップ 5: スクリーンショットを抽出")
        segments = await transcript_service.get_transcript_segments(video_path)
        if segments:
            segments = await transcript_service.filter_important_segments(segments)

        screenshots = await video_processor.extract_key_frames(
            video_path,
            num_screenshots=settings.SCREENSHOT_COUNT
        )
        print(f"  ✅ {len(screenshots)}枚のスクリーンショット抽出完了")

        # 詳細レポート（オプション）
        detailed_report_text = None
        if detailed_report:
            print("\n📊 ステップ 6: Claude による詳細レポート生成")
            detailed_report_text = await claude_summarizer.generate_detailed_report(
                title=video_info.get("title", ""),
                description=video_info.get("description", ""),
                transcript=transcript,
                duration=video_info.get("duration", 0),
            )
            print("  ✅ 詳細レポート完了")

        print("\n📄 ステップ 7: HTML レポート生成")
        html_content = report_generator.generate_html_report(
            title=video_info.get("title", ""),
            description=video_info.get("description", ""),
            duration=video_info.get("duration", 0),
            summary=summary,
            screenshots=screenshots,
            detailed_report=detailed_report_text,
        )

        # ファイル保存
        output_file = f"report-{video_info['title'][:30]}.html"
        output_path = Path(output_file).absolute()
        output_path.write_text(html_content, encoding="utf-8")

        print("=" * 60)
        print("✨ 処理完了！")
        print("=" * 60)
        print(f"\n📄 レポート: {output_path}")
        print(f"\n💡 このレポートは Claude が生成したサマリーを含んでいます")
        print(f"   - API キー不要")
        print(f"   - Claude Code セッション内で処理")
        print(f"   - ローカルファイルとして保存\n")

    except KeyboardInterrupt:
        print("\n\n❌ キャンセルされました\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ エラー: {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
