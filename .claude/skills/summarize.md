---
name: summarize
description: YouTubeビデオをAIでサマライズしてHTMLレポート生成
---

# YouTube Video Summarizer

YouTubeのビデオをAIで自動サマライズして、HTMLレポートを生成するスキル。

## 使用方法

```bash
cd /home/user/video_summarizer
bash summarize.sh "https://www.youtube.com/watch?v=VIDEO_ID"
```

## オプション

- `--detailed`: 詳細レポートも生成
- `-o filename.html`: 出力ファイル名を指定
- `--screenshots N`: スクリーンショット数を指定

## 例

```bash
# 基本的な実行
bash summarize.sh "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# 詳細レポート付き
bash summarize.sh "https://www.youtube.com/watch?v=..." --detailed

# カスタムファイル名
bash summarize.sh "https://www.youtube.com/watch?v=..." -o my_report.html
```

## 出力

実行完了後、HTMLレポートが生成されます：
- `report-[ビデオタイトル].html`

ブラウザで開いて、サマリーとスクリーンショットを確認できます。

## 処理内容

1. **ビデオダウンロード**: yt-dlpで高速ダウンロード
2. **トランスクリプト生成**: Whisper（OpenAI）で音声を自動テキスト化
3. **AIサマリー**: Claude 3.5 Sonnetで要点をまとめる
4. **スクリーンショット**: 話題変化を検出して重要なシーンを自動抽出
5. **HTMLレポート生成**: スタンドアロンの美しいHTMLレポート

## セットアップ

初回のみセットアップが必要です：

```bash
cd /home/user/video_summarizer
cp .env.example .env
# .env を編集してANTHROPIC_API_KEYを設定
bash setup.sh
```

## トラブルシューティング

### 「command not found」エラー

```bash
cd /home/user/video_summarizer
bash setup.sh
```

### 「ANTHROPIC_API_KEY not found」エラー

`.env` ファイルにAPIキーを設定してください：
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### ビデオダウンロード失敗

YouTubeのURLが正しいか確認してください。
短めの動画（5-10分）からテストするのをお勧めします。
