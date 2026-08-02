# YouTube Video Summarizer

YouTubeビデオの内容をAIを使用してサマライズし、スクリーンショット付きで説明するアプリケーションです。

## 機能

- 🎥 **YouTubeビデオのダウンロード**: yt-dlpを使用して高速ダウンロード
- 🗣️ **自動トランスクリプト生成**: OpenAI Whisperを使用した音声認識（日本語対応）
- 📝 **AIサマリー生成**: Claude APIを使用したインテリジェントなテキスト要約
- 📸 **自動スクリーンショット抽出**: ビデオから重要なフレームを自動抽出
- 📊 **詳細レポート生成**: オプションで構造化された詳細分析レポート

## システム要件

- Python 3.10+
- Node.js 16+ (フロントエンド用)
- FFmpeg (ビデオ処理用)

## インストール

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd video_summarizer
```

### 2. バックエンドのセットアップ

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. フロントエンドのセットアップ

```bash
cd frontend
npm install
```

### 4. 環境変数の設定

```bash
cp .env.example .env
```

`.env`ファイルを編集して、APIキーを設定してください：

```
ANTHROPIC_API_KEY=your_actual_api_key
```

## 使用方法

### バックエンド起動

```bash
cd backend
python app.py
```

サーバーは `http://localhost:8000` で起動します。

### フロントエンド起動

別のターミナルウィンドウで：

```bash
cd frontend
npm run dev
```

フロントエンドは `http://localhost:3000` で起動します。

### APIの使用

```bash
curl -X POST http://localhost:8000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=...",
    "include_detailed_report": false
  }'
```

## プロジェクト構造

```
video_summarizer/
├── backend/
│   ├── app.py              # FastAPIアプリケーション
│   ├── config.py           # 設定ファイル
│   ├── requirements.txt    # Python依存関係
│   ├── services/           # ビジネスロジック
│   │   ├── youtube_service.py      # YouTube処理
│   │   ├── video_processor.py      # ビデオ処理
│   │   ├── transcript_service.py   # トランスクリプト生成
│   │   └── summarizer_service.py   # サマリー生成
│   ├── routes/
│   │   └── summarize.py    # APIエンドポイント
│   ├── logs/               # ログファイル
│   └── tmp/                # 一時ファイル
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # メインアプリケーション
│   │   ├── components/
│   │   │   ├── SummaryForm.jsx          # 入力フォーム
│   │   │   ├── SummaryResult.jsx        # 結果表示
│   │   │   ├── ScreenshotGallery.jsx    # スクリーンショット表示
│   │   │   └── LoadingSpinner.jsx       # ローディング表示
│   │   ├── index.css       # スタイル
│   │   └── main.jsx        # エントリーポイント
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
├── .env.example            # 環境変数テンプレート
└── README.md              # このファイル
```

## 主要な依存関係

### バックエンド
- **FastAPI**: 高速なWebフレームワーク
- **yt-dlp**: YouTubeビデオダウンロード
- **openai-whisper**: 音声認識
- **opencv-python**: ビデオ処理
- **anthropic**: Claude API クライアント

### フロントエンド
- **React**: UIフレームワーク
- **Vite**: バンドラー・開発サーバー
- **Tailwind CSS**: スタイリング
- **Axios**: HTTP クライアント

## API仕様

### POST `/api/summarize`

YouTubeビデオをサマライズします。

**リクエスト:**
```json
{
  "url": "https://www.youtube.com/watch?v=...",
  "include_detailed_report": false
}
```

**レスポンス:**
```json
{
  "video_id": "abc123",
  "title": "ビデオタイトル",
  "description": "ビデオの説明",
  "duration": 3600,
  "summary": "サマリー内容",
  "screenshots": ["data:image/jpeg;base64,..."],
  "detailed_report": "詳細レポート（オプション）"
}
```

### GET `/api/health`

ヘルスチェックエンドポイント。

## トラブルシューティング

### FFmpegがインストールされていないエラー

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
choco install ffmpeg
```

### Whisperモデルのダウンロード失敗

Whisperモデルは初回実行時に自動的にダウンロードされます。インターネット接続を確認してください。

### メモリ不足エラー

大きなビデオで処理する場合は、スクリーンショット数を減らすか、ビデオ長を制限してください。

## 設定のカスタマイズ

`backend/config.py`で以下の設定をカスタマイズできます：

- `SCREENSHOT_COUNT`: 抽出するスクリーンショット数（デフォルト: 5）
- `SUMMARY_MAX_TOKENS`: サマリーの最大トークン数（デフォルト: 1000）
- `SCREENSHOT_QUALITY`: スクリーンショットの品質（デフォルト: 85）

## ライセンス

MIT License

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを開いて変更内容を議論してください。
