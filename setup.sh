#!/bin/bash

# YouTube Video Summarizer セットアップスクリプト

echo "🚀 YouTube Video Summarizer セットアップ開始"
echo ""

# Python バージョン確認
echo "📋 Python バージョン確認..."
python3 --version

# バックエンド依存関係をインストール
echo ""
echo "📦 バックエンド依存関係をインストール中..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 環境ファイル作成
if [ ! -f ../.env ]; then
  echo ""
  echo "📝 .envファイルを作成中..."
  cp ../.env.example ../.env
  echo "⚠️  .envファイルを編集してAPIキーを設定してください"
fi

cd ..

# フロントエンド依存関係をインストール
echo ""
echo "📦 フロントエンド依存関係をインストール中..."
cd frontend
npm install

# Tailwind CSS プラグインを追加
npm install --save-dev @tailwindcss/typography

cd ..

echo ""
echo "✅ セットアップ完了！"
echo ""
echo "使用方法："
echo "1. .envファイルにAnthropicのAPIキーを設定"
echo "2. バックエンドを起動: cd backend && source venv/bin/activate && python app.py"
echo "3. フロントエンドを起動: cd frontend && npm run dev"
echo "4. ブラウザで http://localhost:3000 を開く"
echo ""
