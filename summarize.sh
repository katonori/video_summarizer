#!/bin/bash

# YouTube Video Summarizer - ワンコマンド実行スクリプト

if [ -z "$1" ]; then
    echo "使用方法: bash summarize.sh <YouTube URL> [--detailed] [-o output.html]"
    echo ""
    echo "例:"
    echo "  bash summarize.sh https://www.youtube.com/watch?v=..."
    echo "  bash summarize.sh https://www.youtube.com/watch?v=... --detailed"
    echo ""
    exit 1
fi

# venvが存在するか確認
if [ ! -d "backend/venv" ]; then
    echo "⚠️  Python環境が見つかりません。セットアップを実行します..."
    bash setup.sh
fi

# 環境をアクティベート
cd backend
source venv/bin/activate

# CLIを実行
python cli.py "$@"

# 結果ファイルを開く場合（オプション）
# ブラウザで開きたい場合
if command -v xdg-open &> /dev/null; then
    xdg-open "$output_file" 2>/dev/null
elif command -v open &> /dev/null; then
    open "$output_file" 2>/dev/null
fi
