#!/usr/bin/env python3
"""
Claude Code セッション内での実行用スクリプト（フェーズ1: 準備）

ダウンロード・文字起こし・トピック分割・スクリーンショット抽出までを行い、
各トピックの生トランスクリプトを含む「下書きJSON」を出力する。

この下書きは、Claude Code セッション内で Claude 自身がトランスクリプトを
読んで、要約（points）を書き込むためのもの。単なる文の抜き出しではなく、
会話の内容を理解した上での高レベルな要約を作るには、この工程に
実際の言語モデル（今動いているClaude自身）が関わる必要がある。

使い方:
  1. python summarize_prepare.py <URL> --cookies cookies.txt
     → draft-xxxx.json が生成される
  2. Claude Code セッション内で、draft-xxxx.json を読み込み、
     各トピックの "points" に要約（箇条書き、3-5個）を書き込む
  3. python finalize_report.py draft-xxxx.json
     → 最終的なHTMLレポートが生成される
"""

import asyncio
import json
import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from services.youtube_service import YouTubeService
from services.transcript_service import TranscriptService
from services.video_processor import VideoProcessor
from services.topic_summarizer import build_topics
from config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


async def main():
    if len(sys.argv) < 2:
        print("""
使用方法:
  python summarize_prepare.py <YouTube URL> [--cookies cookies.txt]

このスクリプトはダウンロード・文字起こし・トピック分割・スクリーンショット
抽出までを行い、下書きJSON（draft-xxxx.json）を出力します。

次のステップ:
  1. Claude Code セッション内で draft-xxxx.json を読み込む
  2. 各トピックの "points" に、会話の内容を理解した上での
     高レベルな要約（箇条書き）を書き込む（生の発言をそのまま
     コピーするのではなく、内容をまとめ直す）
  3. python finalize_report.py draft-xxxx.json でHTMLレポート生成
""")
        sys.exit(1)

    url = sys.argv[1]

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
        print("🚀 フェーズ1: 準備を開始します")
        print("=" * 60)

        youtube_service = YouTubeService(settings.PROCESSING_DIR, cookie_file=cookie_file)
        transcript_service = TranscriptService()
        video_processor = VideoProcessor(settings.PROCESSING_DIR)

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
        print(f"  ✅ 検出言語: {transcript_service.detected_language}")

        print("\n🔖 ステップ 4: トピックに分割")
        topics = build_topics(video_info, segments)
        print(f"  ✅ {len(topics)}個のトピックを検出")

        print("\n📸 ステップ 5: トピックごとにスクリーンショットを抽出")
        for topic in topics:
            capture_time = min(topic["start"] + 2, max(topic["end"] - 1, topic["start"]))
            topic["image"] = await video_processor.extract_frame_at_time(video_path, capture_time)
        extracted = sum(1 for t in topics if t.get("image"))
        print(f"  ✅ {extracted}/{len(topics)}枚のスクリーンショット抽出完了")

        print("\n📝 ステップ 6: 下書きJSONを生成")
        for topic in topics:
            start, end = topic["start"], topic["end"]
            seg_texts = [
                (seg.get("text") or "").strip()
                for seg in segments
                if start <= seg.get("start", 0) < end and (seg.get("text") or "").strip()
            ]
            topic["transcript"] = "".join(seg_texts)
            topic["points"] = None  # ここに Claude が要約を書き込む

        draft = {
            "title": video_info.get("title", ""),
            "description": video_info.get("description", ""),
            "duration": video_info.get("duration", 0),
            "topics": topics,
        }

        safe_title = "".join(c for c in video_info["title"][:40] if c.isalnum() or c in " -_").strip()
        draft_path = Path(f"draft-{safe_title or video_id}.json").absolute()
        draft_path.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")

        print("=" * 60)
        print("✨ フェーズ1 完了！")
        print("=" * 60)
        print(f"\n📄 下書きファイル: {draft_path}\n")
        print("次のステップ（Claude Code セッション内で）:")
        print(f"  1. 「{draft_path.name} を読んで、各トピックの points を")
        print(f"     高レベルな要約で埋めて」と Claude に依頼する")
        print(f"  2. python finalize_report.py {draft_path.name}\n")

    except KeyboardInterrupt:
        print("\n\n❌ キャンセルされました\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ エラー: {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
