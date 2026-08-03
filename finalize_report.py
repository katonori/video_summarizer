#!/usr/bin/env python3
"""
Claude Code セッション内での実行用スクリプト（フェーズ2: 仕上げ）

summarize_prepare.py が生成した下書きJSON（各トピックの points が
Claude によって埋められたもの）を読み込み、最終的なHTMLレポートを生成する。
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from services.report_generator import ReportGenerator


def main():
    if len(sys.argv) < 2:
        print("""
使用方法:
  python finalize_report.py <draft.json> [出力ファイル名]

draft.json は summarize_prepare.py で生成し、各トピックの "points" を
Claude が埋めたものを指定してください。
""")
        sys.exit(1)

    draft_path = Path(sys.argv[1])
    if not draft_path.exists():
        print(f"❌ ファイルが見つかりません: {draft_path}")
        sys.exit(1)

    data = json.loads(draft_path.read_text(encoding="utf-8"))
    topics = data.get("topics", [])

    missing = [t.get("title", "?") for t in topics if not t.get("points")]
    if missing:
        print("❌ 以下のトピックの points がまだ埋まっていません:")
        for m in missing:
            print(f"   - {m}")
        print("\nClaude Code セッション内で draft JSON の points を埋めてから再実行してください。")
        sys.exit(1)

    html_content = ReportGenerator.generate_html_report(
        title=data.get("title", ""),
        description=data.get("description", ""),
        duration=data.get("duration", 0),
        summary="",
        screenshots=[],
        topics=topics,
    )

    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        output_file = f"report-{data.get('title', 'video')[:30]}.html"

    output_path = Path(output_file).absolute()
    output_path.write_text(html_content, encoding="utf-8")

    print(f"✅ レポート生成完了: {output_path}")


if __name__ == "__main__":
    main()
