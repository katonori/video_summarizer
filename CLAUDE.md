# YouTube Video Summarizer - Claude Code Configuration

このファイルはClaude Codeプロジェクトの設定です。

## 概要

YouTubeビデオをAIで自動サマライズし、HTML報告書を生成するツール。

## 主な機能

- 🎥 YouTubeビデオのダウンロード
- 🗣️ 音声をテキスト化（Whisper）
- 📝 AIでサマリー生成（Claude）
- 📸 重要シーン自動抽出
- 📄 HTMLレポート生成

## 実行方法

### クイック実行（推奨）

```bash
cd /home/user/video_summarizer
bash summarize.sh "https://www.youtube.com/watch?v=..."
```

### オプション

```bash
# 詳細レポート付き
bash summarize.sh "URL" --detailed

# カスタムファイル名
bash summarize.sh "URL" -o report.html

# スクリーンショット数を指定
cd backend && source venv/bin/activate
python cli.py "URL" --screenshots 10
```

## 初期セットアップ

```bash
cd /home/user/video_summarizer

# 環境変数設定
cp .env.example .env
# .env を編集して ANTHROPIC_API_KEY を設定

# 依存関係インストール
bash setup.sh
```

## ファイル構成

```
backend/
  ├── cli.py                 # CLIツール（メイン実行ファイル）
  ├── app.py                 # FastAPI サーバー
  ├── config.py              # 設定
  ├── services/              # ビジネスロジック
  │   ├── youtube_service.py
  │   ├── video_processor.py (シーン検出)
  │   ├── transcript_service.py
  │   ├── summarizer_service.py
  │   └── report_generator.py (HTML生成)
  └── routes/summarize.py    # API

frontend/
  └── src/App.jsx            # Web UI（オプション）
```

## コマンドリファレンス

### 基本的な実行

```bash
cd /home/user/video_summarizer
bash summarize.sh "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Pythonで直接実行

```bash
cd /home/user/video_summarizer/backend
source venv/bin/activate
python cli.py "https://www.youtube.com/watch?v=..." --detailed --screenshots 5
```

### ウェブUIで実行

```bash
# バックエンド起動（ターミナル1）
cd /home/user/video_summarizer/backend
source venv/bin/activate
python app.py

# フロントエンド起動（ターミナル2）
cd /home/user/video_summarizer/frontend
npm run dev

# ブラウザで http://localhost:3000 を開く
```

## 環境変数

```
ANTHROPIC_API_KEY     # 必須: Anthropic API キー
SCREENSHOT_COUNT      # スクリーンショット数 (デフォルト: 5)
SUMMARY_MAX_TOKENS    # サマリーの最大トークン数 (デフォルト: 1000)
```

## 出力

実行後、HTML報告書が生成されます：

```
report-[ビデオタイトル].html
```

このファイルには以下が含まれます：
- ビデオタイトル・説明
- サマリー
- 抽出されたスクリーンショット（5枚）
- 詳細レポート（オプション）

## トラブルシューティング

### 「command not found」

```bash
cd /home/user/video_summarizer
bash setup.sh  # セットアップ実行
bash summarize.sh "URL"
```

### APIキーエラー

```bash
cd /home/user/video_summarizer
# .env ファイルを確認
cat .env

# ANTHROPIC_API_KEY が設定されているか確認
export ANTHROPIC_API_KEY="sk-..."
```

### メモリ不足

スクリーンショット数を減らします：

```bash
python cli.py "URL" --screenshots 3
```

## 依存関係

### バックエンド (Python)
- FastAPI: Web フレームワーク
- yt-dlp: ビデオダウンロード
- openai-whisper: 音声認識
- anthropic: Claude API
- opencv-python: フレーム処理
- Pillow: 画像処理

### フロントエンド (Node.js)
- React
- Vite
- Tailwind CSS

## 実装の詳細

### シーン検出アルゴリズム

1. ビデオをサンプリング（毎秒1フレーム程度）
2. 連続フレーム間の色差を計算
3. 色差が大きいフレーム（シーン変化）を検出
4. スコアが高い順にトップNフレームを抽出

### トランスクリプト

OpenAI Whisperの`base`モデルを使用し、日本語に対応。

### サマリー

Claude 3.5 Sonnetを使用して、要点をピックアップした日本語要約を生成。

### HTML レポート

外部CDN不要のスタンドアロンHTML。
Base64エンコードされた画像を埋め込み。
印刷とオフライン表示に対応。

## ライセンス

MIT License

## 問い合わせ

実装に関する質問やバグ報告は、プロジェクトのIssueセクションまで。
