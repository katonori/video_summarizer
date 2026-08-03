---
name: summarize
description: YouTubeビデオをトピックごとに要約し、スクリーンショット付きHTMLレポートを生成
---

# YouTube Video Summarizer

YouTubeのビデオをトピック（チャプター）ごとに要約し、スクリーンショット付きの
HTMLレポートを生成するスキル。**Anthropic APIキーは不要。** 要約は Claude（今の
セッション自身）がトランスクリプトを読んで作成するため、外部APIを呼ばない。

## このスキルが呼ばれたら、Claude が行うこと

ユーザーから YouTube の URL（と、必要ならクッキーファイルのパス）を受け取ったら、
以下をすべて **自分で（Bash/Read/Edit ツールを使って）実行し、完了させる。**
ユーザーに手作業（ファイルのアップロードや中間ファイルの受け渡し）をさせない。

### ステップ1: フェーズ1スクリプトを実行（ダウンロード・文字起こし・トピック分割）

```bash
cd /home/user/video_summarizer
python3 summarize_prepare.py "<URL>" [--cookies <cookie_file>]
```

これで `draft-<タイトル>.json` が生成される。ボット認証エラーが出た場合は、
ユーザーにクッキーファイルのパスを尋ねて `--cookies` オプションを付けて再実行する。

### ステップ2: 下書きJSONを読み、要点を自分で書き込む

生成された `draft-*.json` を Read ツールで読む（サイズが大きい場合は `image`
フィールドを除いて確認するか、`jq` や python で `topics[].transcript` だけを
抽出して読む）。

各トピックについて、**`transcript` フィールドの生の発言をそのまま引用するのでは
なく**、内容を理解した上で3〜4個の高レベルな要点（日本語、簡潔な文）を考え、
Edit ツールでそのトピックの `"points": null` を実際のリスト
`"points": ["要点1", "要点2", "要点3"]` に書き換える。全トピック分を埋めるまで
繰り返す。

要点を書くときの基準:
- 誰が何と言ったかの引用ではなく、「何が起きている／何が主張されているか」を
  まとめ直す
- 各トピック内で異なる観点をカバーする（同じ内容の言い換えを繰り返さない）
- 数字・固有名詞・具体的な結論など、情報として意味のある部分は残す

### ステップ3: フェーズ2スクリプトを実行してHTMLを生成

全トピックの `points` を埋め終えたら:

```bash
python3 finalize_report.py "draft-<タイトル>.json"
```

`points` が埋まっていないトピックがあるとこのスクリプトはエラーで教えてくれるので、
その場合はステップ2に戻って埋め切る。

### ステップ4: 完了報告

生成された `report-*.html` のパスをユーザーに伝える。可能であれば
SendUserFile などで送付する。

## オプション

- `--cookies <file>`: YouTube のボット認証を回避するためのクッキーファイル
  （`Sign in to confirm you're not a bot` エラーが出た場合に必要）

## トラブルシューティング

### `ffmpeg` が見つからない

```bash
cd /home/user/video_summarizer
bash setup_cpu.sh
```

### `Requested format is not available` / 認証エラー

YouTube 側のボット対策の可能性が高い。ユーザーにブラウザ拡張機能などで
エクスポートした `cookies.txt` を用意してもらい、`--cookies` オプションで渡す。

### GPU がない環境

`backend/requirements.txt` は CPU 版 PyTorch を想定しているため、そのまま
`setup_cpu.sh` でセットアップすれば動作する。
