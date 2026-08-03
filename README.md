# YouTube Video Summarizer

YouTubeビデオをAIで自動サマライズし、HTML報告書を生成するアプリケーションです。

## 機能

- 🎥 **YouTubeビデオのダウンロード**: yt-dlpで高速ダウンロード
- 🗣️ **自動トランスクリプト生成**: OpenAI Whisper（日本語対応）
- 📝 **AIサマリー生成**: Claude 3.5 Sonnet
- 📸 **重要シーン自動抽出**: フレーム間の色差分析で重要な箇所を自動検出
- 📊 **HTML報告書生成**: 美しくフォーマットされたスタンドアロンHTML

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

**GPUがない環境（推奨方法）:**

```bash
cd /home/user/video_summarizer
bash setup_cpu.sh
```

**手動セットアップ:**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# CPU版 PyTorch をインストール
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# その他の依存パッケージをインストール
pip install -r requirements.txt
```

**GPU環境の場合:**

```bash
cd backend
python -m venv venv
source venv/bin/activate

# GPU版 PyTorch をインストール（CUDA 11.8対応）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# その他の依存パッケージをインストール
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

`.env`ファイルにAPIキーを設定：

```
ANTHROPIC_API_KEY=your_actual_api_key
```

## 使用方法

### 方法1: Claude Code セッション内での実行（推奨）

```bash
cd /home/user/video_summarizer
python3 summarize_in_claude.py "https://www.youtube.com/watch?v=..."
```

**クッキーを使用する場合:**

```bash
python3 summarize_in_claude.py "https://www.youtube.com/watch?v=..." --cookies cookies.txt
```

**詳細レポート付き:**

```bash
python3 summarize_in_claude.py "https://www.youtube.com/watch?v=..." --cookies cookies.txt --detailed
```

**特徴:**
- API キー不要
- Claude Code セッション内で直接処理
- Claude が自動的にテキスト分析を行う
- GPU不要（CPU版で動作）

### 方法2: CLI コマンド

```bash
bash summarize.sh "https://www.youtube.com/watch?v=..."
```

### 方法3: Web UI（オプション）

```bash
# バックエンド起動
cd backend
python app.py

# フロントエンド起動（別ターミナル）
cd frontend
npm run dev
```

ブラウザで `http://localhost:3000` を開く

### 方法4: Python 直接実行

```bash
cd backend
source venv/bin/activate
python cli.py "https://www.youtube.com/watch?v=..."
```

### API の使用例

```bash
# HTMLレポート生成
curl -X POST http://localhost:8000/api/summarize-html \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=...",
    "include_detailed_report": false
  }' \
  > report.html

# JSON形式での取得
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
│   ├── app.py                      # FastAPI メインアプリケーション
│   ├── config.py                   # 設定
│   ├── requirements.txt            # Python依存関係
│   ├── services/
│   │   ├── youtube_service.py      # ビデオダウンロード
│   │   ├── video_processor.py      # キーフレーム抽出
│   │   ├── transcript_service.py   # トランスクリプト生成
│   │   ├── summarizer_service.py   # AI要約
│   │   ├── report_generator.py     # HTMLレポート生成
│   │   └── __init__.py
│   ├── routes/
│   │   └── summarize.py            # API エンドポイント
│   ├── logs/
│   └── tmp/
├── frontend/
│   ├── src/
│   │   ├── App.jsx                 # メインコンポーネント
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
├── .env.example                    # 環境変数テンプレート
└── README.md
```

## API仕様

### POST `/api/summarize-html`

YouTubeビデオをサマライズしてHTMLレポートを返します。

**リクエスト:**
```json
{
  "url": "https://www.youtube.com/watch?v=...",
  "include_detailed_report": false
}
```

**レスポンス:** HTML content (Content-Type: text/html)

### POST `/api/summarize`

YouTubeビデオをサマライズしてJSONで返します。

**レスポンス:**
```json
{
  "video_id": "abc123",
  "title": "ビデオタイトル",
  "description": "説明",
  "duration": 3600,
  "summary": "サマリー内容",
  "screenshots": ["data:image/jpeg;base64,..."],
  "detailed_report": null
}
```

### GET `/api/health`

ヘルスチェック。

## キーフレーム抽出について

アプリケーションは以下のアルゴリズムでビデオから重要なシーンを自動選定します：

1. 動画を一定間隔でサンプリング
2. 連続するフレーム間の色差を計算
3. 色差が大きい（シーン変化が大きい）フレームを検出
4. スコアが高い順にトップNフレームを選択

これにより、単純な時間分割ではなく、実際に内容が変わった重要なシーンが抽出されます。

## トラブルシューティング

### FFmpegがインストールされていない

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
choco install ffmpeg
```

### Whisperモデルのダウンロード失敗

初回実行時に自動ダウンロードされます。インターネット接続を確認してください。

### メモリ不足

大きなビデオの場合、`backend/config.py`の`SCREENSHOT_COUNT`を減らしてください。

## 設定のカスタマイズ

`backend/config.py`で調整可能：

- `SCREENSHOT_COUNT`: 抽出するスクリーンショット数（デフォルト: 5）
- `SUMMARY_MAX_TOKENS`: サマリーの最大トークン数（デフォルト: 1000）
- `SCREENSHOT_QUALITY`: 画質（デフォルト: 85）
- `MAX_VIDEO_DURATION`: 処理対象の最大ビデオ長（秒）

## ライセンス

MIT License
