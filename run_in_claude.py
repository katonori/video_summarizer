#!/usr/bin/env python3
"""
Claude Code から直接実行用スクリプト
/summarize コマンドから呼び出される
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("❌ 使用方法: /summarize https://www.youtube.com/watch?v=...")
        print("\n例:")
        print("  /summarize https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        print("  /summarize https://www.youtube.com/watch?v=... --detailed")
        sys.exit(1)

    # YouTubeビデオURLを取得
    url = sys.argv[1]

    # その他のオプションを取得
    options = sys.argv[2:] if len(sys.argv) > 2 else []

    # 作業ディレクトリ
    project_dir = Path(__file__).parent
    os.chdir(project_dir)

    print("\n" + "=" * 60)
    print("🎬 YouTube Video Summarizer - Claude Code Integration")
    print("=" * 60)
    print(f"\n📹 ビデオURL: {url}")
    if options:
        print(f"📋 オプション: {' '.join(options)}")
    print()

    # CLIスクリプトを実行
    cmd = ["bash", "summarize.sh", url] + options

    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 60)
        print("✅ 処理完了！")
        print("=" * 60)
        print("\n💡 生成されたレポートは Claude Code で確認できます")
        print("   または、以下の場所に保存されています:")
        print(f"   {project_dir}\n")
        sys.exit(0)

    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print(f"❌ エラーが発生しました (終了コード: {e.returncode})")
        print("=" * 60)
        print("\n🔧 トラブルシューティング:")
        print("  1. .env ファイルに ANTHROPIC_API_KEY が設定されているか確認")
        print("  2. YouTubeのURLが正しいか確認")
        print("  3. インターネット接続を確認")
        print("  4. 依存関係がインストールされているか確認: bash setup.sh")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n❌ キャンセルされました\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
