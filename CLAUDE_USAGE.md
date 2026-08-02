# Claude Codeでの使用方法

このプロジェクトをClaude Codeから直接実行できます。

## クイックスタート

### 方法1: CLIコマンド（推奨）

```bash
cd /home/user/video_summarizer
bash summarize.sh "https://www.youtube.com/watch?v=..."
```

例：
```bash
bash summarize.sh "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### 方法2: 詳細レポート付き

```bash
bash summarize.sh "https://www.youtube.com/watch?v=..." --detailed
```

### 方法3: カスタムファイル名で出力

```bash
bash summarize.sh "https://www.youtube.com/watch?v=..." -o my_report.html
```

## Python CLIの直接実行

```bash
cd /home/user/video_summarizer/backend
source venv/bin/activate
python cli.py "https://www.youtube.com/watch?v=..." --detailed
```

## セットアップ（初回のみ）

環境変数を設定してください：

```bash
cd /home/user/video_summarizer
cp .env.example .env
```

`.env`ファイルにAPIキーを追加：
```
ANTHROPIC_API_KEY=your_anthropic_api_key
```

その後：
```bash
bash setup.sh
```

## 出力結果

実行すると以下のような結果が表示されます：

```
🎬 YouTube Video Summarizer
==================================================

📥 ビデオ情報を取得中...

✅ タイトル: ビデオのタイトル
✅ 長さ: 1234秒

⏳ ビデオをダウンロード中...

✅ ダウンロード完了

⏳ トランスクリプトを生成中...

✅ トランスクリプト完了（12345文字）

⏳ AIでサマライズ中...

✅ サマリー完了

⏳ キーフレームを抽出中（5枚）...

✅ 5枚のスクリーンショット抽出完了

📝 HTMLレポートを生成中...

✅ HTMLレポート保存完了

==================================================

📄 出力ファイル: /path/to/report-video-title.html

✨ レポートを以下で確認できます:
   file:///path/to/report-video-title.html
```

## トラブルシューティング

### 「module not found」エラー

```bash
cd /home/user/video_summarizer/backend
source venv/bin/activate
pip install -r requirements.txt
```

### 「ANTHROPIC_API_KEY not found」エラー

`.env`ファイルを確認して、APIキーが設定されているか確認してください。

### ビデオダウンロード失敗

YouTubeのURL形式を確認してください：
- ✅ `https://www.youtube.com/watch?v=...`
- ✅ `https://youtu.be/...`
- ✅ `https://www.youtube.com/shorts/...`

## 高度な設定

### スクリーンショット数の変更

```bash
cd /home/user/video_summarizer/backend
python cli.py "URL" --screenshots 10
```

### 出力ファイルの指定

```bash
python cli.py "URL" -o ~/Downloads/my_summary.html
```

## 実装の詳細

- **トランスクリプト**: OpenAI Whisper（日本語対応）
- **サマリー**: Claude 3.5 Sonnet
- **スクリーンショット**: フレーム差分分析で自動抽出
- **レポート**: スタンドアロンHTML（外部依存なし）

すべてのファイルはローカルで処理されます。
