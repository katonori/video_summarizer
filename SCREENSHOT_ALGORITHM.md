# スクリーンショット抽出アルゴリズム

## 問題：「色差分析」だけでは不十分

### 従来の方法（色差分析のみ）
```
フレーム A  →  フレーム B
色が大きく変わった？
  YES → スクリーンショット対象 ✅
  NO  → スキップ ❌
```

**問題:**
- ❌ ライトが点灯した → 検出（無関係）
- ❌ カット編集 → 検出（内容変化なし）
- ❌ グラフが表示 → 検出しない（色差小さい）
- ✅ スライド切替 → 検出（内容変化）

## 解決：トランスクリプト + 複合分析

### 改善後の方法

```
ビデオ
  ↓
Whisper でトランスクリプト生成
  ↓
セグメント分割（話題ごと）
  ↓
セグメント間の「話題変化度」を計算
  ↓
「話題が大きく変わった時点」を検出
  ↓
その時点のフレームをキャプチャ
  ↓
フォールバック：色差分析でフィルタリング
```

## アルゴリズム詳細

### ステップ1: トランスクリプトセグメント取得

```python
result = whisper.transcribe(video_path)
segments = [
    {
        "start": 0.0,      # 開始時間（秒）
        "end": 5.2,        # 終了時間（秒）
        "text": "今日のテーマは..."  # 発話内容
    },
    {
        "start": 5.2,
        "end": 12.1,
        "text": "次にグラフを見てみましょう"
    },
    ...
]
```

### ステップ2: セグメント間の「話題変化度」を計算

```python
def text_similarity(text1, text2):
    """ジャッカード類似度で計算"""
    words1 = set(text1.split())
    words2 = set(text2.split())
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union  # 0.0 ~ 1.0

# 例：
text1 = "今日のテーマは予算についてです"
text2 = "予算の詳細を見てみましょう"
similarity = 0.33  # 共通単語：["予算"]

# スコア = 1.0 - 類似度
score = 0.67  # 話題が変わった度合い（高いほど重要）
```

### ステップ3: スコアが高いセグメントを選択

```
セグメント1: "イントロ"           → スコア 1.0 ✅
セグメント2: "テーマ説明"          → スコア 0.45
セグメント3: "グラフ表示"          → スコア 0.68 ✅
セグメント4: "グラフ解説"          → スコア 0.35
セグメント5: "次のテーマ"          → スコア 0.72 ✅
セグメント6: "まとめ"             → スコア 0.51

↓ スコアが高い順にトップ5を選択
↓ ビデオ内で時系列でソート

抽出フレーム: [1.0秒, 12.1秒, 25.3秒]
```

### ステップ4: フォールバック（色差分析）

セグメント数が不足する場合、従来の色差分析でフレームを補足：

```python
if len(selected_frames) < num_screenshots:
    # 色差分析でフォールバック
    fallback_frames = extract_by_scene_change(...)
```

## 実装例

### 基本的な使用

```python
from services import SmartScreenshot, TranscriptService

transcript_service = TranscriptService()
smart_screenshot = SmartScreenshot(output_dir)

# トランスクリプト取得
segments = await transcript_service.get_transcript_segments(video_path)
segments = await transcript_service.filter_important_segments(segments)

# スマートスクリーンショット抽出
screenshots = await smart_screenshot.extract_by_transcript(
    video_path,
    segments=segments,
    num_screenshots=5
)
```

## 検出精度の改善

### セグメントフィルタリング

```python
# 最小文字数でフィルタリング
# → 「ああ」「えっと」などの無意味なセグメントを除外
filtered_segments = await transcript_service.filter_important_segments(
    segments,
    min_length=15  # 15文字以上
)
```

### テキスト類似度の仕組み

```
セグメント1: "AIについて説明します"
セグメント2: "AIの定義を見ていきます"

共通単語: ["について", "ます", "を", "ます"] → ["について"]
類似度: 1/4 = 0.25
スコア: 1.0 - 0.25 = 0.75 ✅（話題が継続）

セグメント3: "次は機械学習です"

共通単語: [] 
類似度: 0/7 = 0.0
スコア: 1.0 - 0.0 = 1.0 ✅✅（話題が大きく変わった）
```

## パフォーマンス

| 段階 | 処理時間 | 説明 |
|------|---------|------|
| 1. ビデオダウンロード | 1-10分 | YouTubeサイズに依存 |
| 2. Whisper処理 | 5-15分 | ビデオ長に依存（リアルタイム処理） |
| 3. セグメント分析 | <1秒 | 単純な文字列処理 |
| 4. スクリーンショット抽出 | 5秒 | フレーム読込5回分 |

**合計: 11-26分**（ビデオ長と回線速度に依存）

## カスタマイズ

### スクリーンショット数の変更

```bash
python cli.py "URL" --screenshots 10  # 10枚に増やす
```

### セグメントフィルタリング強度を調整

`backend/services/transcript_service.py`:
```python
await transcript_service.filter_important_segments(
    segments,
    min_length=30  # 30文字以上（より厳しい）
)
```

## 今後の改善案

- [ ] **OCR**: スライドのテキスト認識で検出精度向上
- [ ] **顔検出**: 話者変化を検出
- [ ] **物体検出**: グラフ、図表の出現を検出
- [ ] **エッジ検出**: 重要な視覚情報の変化を検出
- [ ] **言語モデル**: テキスト内容から重要度を判定

## 参考資料

- Whisper: https://github.com/openai/whisper
- Jaccard類似度: https://ja.wikipedia.org/wiki/ジャッカード指数
