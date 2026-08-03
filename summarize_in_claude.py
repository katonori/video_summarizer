#!/usr/bin/env python3
"""
Claude Code セッション内での実行用スクリプト

外部 API (Anthropic API) へのアクセスは不要です。
トピック（動画のチャプター、なければ自動区切り）ごとに
トランスクリプトから要約とスクリーンショットを生成します。
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
from services.topic_summarizer import summarize_by_topic
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
  python summarize_in_claude.py <YouTube URL> [OPTIONS]

例:
  python summarize_in_claude.py "https://www.youtube.com/watch?v=..."
  python summarize_in_claude.py "https://www.youtube.com/watch?v=..." --cookies cookies.txt

オプション:
  --cookies <file>        YouTubeアクセス用のクッキーファイル

特徴:
  ✓ API キー不要（ローカル処理のみ）
  ✓ トピックごとに要約とスクリーンショットを生成
  ✓ ビデオダウンロード＆トランスクリプト＆サマリーを一度に実行

処理フロー:
  1. YouTubeビデオのメタデータ取得
  2. ビデオファイルをダウンロード
  3. Whisper でトランスクリプト生成
  4. トピック（チャプター）ごとに区切って要約
  5. トピックごとにスクリーンショットを抽出
  6. HTML レポート生成
""")
        sys.exit(1)

    url = sys.argv[1]

    # クッキーファイルをコマンドラインから取得
    cookie_file = None
    if "--cookies" in sys.argv:
        idx = sys.argv.index("--cookies")
        if idx + 1 < len(sys.argv):
            cookie_path = Path(sys.argv[idx + 1])
            if cookie_path.exists():
                cookie_file = cookie_path
            else:
                print(f"❌ クッキーファイルが見つかりません: {cookie_path}")

    try:
        print("\n" + "=" * 60)
        print("🚀 処理を開始します")
        print("=" * 60)

        # 初期化
        youtube_service = YouTubeService(settings.PROCESSING_DIR, cookie_file=cookie_file)
        transcript_service = TranscriptService()
        video_processor = VideoProcessor(settings.PROCESSING_DIR)
        report_generator = ReportGenerator()

        print("\n📡 ステップ 1: ビデオ情報を取得")
        video_info = await youtube_service.get_video_info(url)
        if not video_info:
            raise Exception("ビデオ情報の取得に失敗しました")

        print(f"  ✅ タイトル: {video_info['title']}")
        print(f"  ✅ 長さ: {int(video_info['duration'])}秒")

        print("\n⬇️  ステップ 2: ビデオをダウンロード")
        video_id = video_info.get("id") or youtube_service.extract_video_id(url) or "claude_video"
        video_path = await youtube_service.download_video(url, video_id)
        if not video_path:
            raise Exception("ビデオのダウンロードに失敗しました")
        print(f"  ✅ ダウンロード完了: {video_path}")

        print("\n🗣️  ステップ 3: トランスクリプトを生成 (Whisper)")
        segments = await transcript_service.get_transcript_segments(video_path)
        if not segments:
            raise Exception("トランスクリプトの生成に失敗しました")
        segments = await transcript_service.filter_important_segments(segments)
        total_chars = sum(len(seg.get("text", "")) for seg in segments)
        print(f"  ✅ トランスクリプト完了: {len(segments)}セグメント / {total_chars}文字")

        print("\n📝 ステップ 4: トピックごとに要約を生成")
        topics = summarize_by_topic(video_info, segments)
        print(f"  ✅ {len(topics)}個のトピックを検出")
        for t in topics:
            print(f"     - [{int(t['start'])}s] {t['title']}")

        print("\n📸 ステップ 5: トピックごとにスクリーンショットを抽出")
        for topic in topics:
            # チャプター開始直後（+2秒）のフレームを使用
            capture_time = min(topic["start"] + 2, max(topic["end"] - 1, topic["start"]))
            topic["image"] = await video_processor.extract_frame_at_time(video_path, capture_time)
        extracted = sum(1 for t in topics if t.get("image"))
        print(f"  ✅ {extracted}/{len(topics)}枚のスクリーンショット抽出完了")

        print("\n📄 ステップ 6: HTML レポート生成")
        html_content = report_generator.generate_html_report(
            title=video_info.get("title", ""),
            description=video_info.get("description", ""),
            duration=video_info.get("duration", 0),
            summary="",
            screenshots=[],
            topics=topics,
        )

        # ファイル保存
        output_file = f"report-{video_info['title'][:30]}.html"
        output_path = Path(output_file).absolute()
        output_path.write_text(html_content, encoding="utf-8")

        print("=" * 60)
        print("✨ 処理完了！")
        print("=" * 60)
        print(f"\n📄 レポート: {output_path}\n")

    except KeyboardInterrupt:
        print("\n\n❌ キャンセルされました\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ エラー: {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
