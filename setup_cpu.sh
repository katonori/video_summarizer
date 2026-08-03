#!/bin/bash
set -e

echo "🚀 YouTube Video Summarizer のセットアップを開始"
echo "=============================================="

# Python仮想環境のセットアップ
echo ""
echo "📦 Python仮想環境を作成中..."
cd "$(dirname "$0")/backend"
python3 -m venv venv
source venv/bin/activate

# CPU版 PyTorch のインストール
echo ""
echo "🔧 CPU版PyTorchをインストール中..."
pip install --upgrade pip setuptools wheel
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 依存パッケージのインストール
echo ""
echo "📚 依存パッケージをインストール中..."
pip install -r requirements.txt

echo ""
echo "✅ セットアップ完了！"
echo ""
echo "使用方法:"
echo "  cd /home/user/video_summarizer"
echo "  python3 summarize_in_claude.py 'https://www.youtube.com/watch?v=...' --cookies cookies.txt"
echo ""
