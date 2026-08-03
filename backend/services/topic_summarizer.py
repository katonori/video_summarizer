"""
トピックごとのサマリー生成（API不要のローカル処理）

- 動画説明欄のチャプター（タイムスタンプ）があればそれをトピック境界として利用
- なければトランスクリプトのセグメントから均等にトピックを自動生成
- 各トピック区間のトランスクリプトから単語頻度ベースの抽出型要約を生成
"""

import re
import logging
from collections import Counter
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

TIMESTAMP_RE = re.compile(r"^\s*(?:(\d{1,2}):)?(\d{1,2}):(\d{2})\s+(\S.*?)\s*$")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[。！？\.\!\?])\s*")
WORD_RE = re.compile(r"[一-龥ぁ-んァ-ヶa-zA-Z0-9]{2,}")

STOPWORDS = {
    "の", "に", "は", "を", "た", "が", "で", "て", "と", "し", "れ", "さ", "ある", "いる",
    "も", "する", "から", "な", "こと", "として", "い", "や", "れる", "など", "なっ", "ない",
    "この", "ため", "その", "あっ", "よう", "また", "もの", "という", "あり", "まで", "られ",
    "なる", "へ", "か", "だ", "これ", "によって", "により", "おり", "より", "による", "ず",
    "なり", "られる", "において", "ば", "なかっ", "なく", "しかし", "について", "せ", "だっ",
    "できる", "それ", "う", "ので", "なお", "のみ", "でき", "き", "つ", "における", "および",
    "いう", "さらに", "でも", "ら", "たり", "に関する", "たち", "ます", "ん", "なら", "です",
    "the", "a", "an", "to", "of", "in", "and", "is", "that", "it", "for", "on", "with",
    "as", "are", "this", "be", "was", "were", "by", "at", "from", "or", "you", "your",
}


def parse_chapters(description: str) -> List[Dict]:
    """動画説明欄からチャプター（タイムスタンプ + タイトル）を抽出"""
    chapters = []
    if not description:
        return chapters

    for line in description.splitlines():
        match = TIMESTAMP_RE.match(line)
        if not match:
            continue
        hours, minutes, seconds, title = match.groups()
        total_seconds = (int(hours) * 3600 if hours else 0) + int(minutes) * 60 + int(seconds)
        title = title.strip()
        if title:
            chapters.append({"start": float(total_seconds), "title": title})

    # チャプターらしきものが2件未満、または時系列順でない場合は誤検出とみなす
    if len(chapters) < 2:
        return []
    chapters.sort(key=lambda c: c["start"])
    return chapters


def _auto_detect_topics(segments: List[Dict], duration: float, target_count: int = 6) -> List[Dict]:
    """チャプターがない場合、時間軸で均等に分割してトピックを生成"""
    if duration <= 0:
        return [{"start": 0.0, "title": "サマリー"}]

    target_count = max(1, min(target_count, int(duration // 90) or 1))
    chunk_len = duration / target_count

    boundaries = []
    for i in range(target_count):
        start = i * chunk_len
        title = None
        for seg in segments or []:
            if seg.get("start", 0) >= start:
                text = (seg.get("text") or "").strip()
                if text:
                    title = text[:20] + ("…" if len(text) > 20 else "")
                break
        boundaries.append({"start": start, "title": title or f"パート{i + 1}"})
    return boundaries


def build_topics(video_info: Dict, segments: Optional[List[Dict]]) -> List[Dict]:
    """動画情報とセグメントからトピック境界（開始・終了・タイトル）のリストを作成"""
    description = video_info.get("description", "") or ""
    duration = float(video_info.get("duration", 0) or 0)

    chapters = parse_chapters(description)
    boundaries = chapters if chapters else _auto_detect_topics(segments or [], duration)

    topics = []
    for i, boundary in enumerate(boundaries):
        start = boundary["start"]
        end = boundaries[i + 1]["start"] if i + 1 < len(boundaries) else duration
        topics.append({"title": boundary["title"], "start": start, "end": max(end, start)})
    return topics


def extract_key_points(text: str, max_points: int = 4, min_length: int = 6) -> List[str]:
    """
    単語頻度スコアに基づき、内容が重複しない要点をいくつか抽出する（外部API不要）

    セリフをそのまま1つの文章として繋げるのではなく、要点ごとに独立した
    箇条書き項目として返す。近い内容の文は重複とみなして除外する（簡易MMR）。
    """
    text = (text or "").strip()
    if not text:
        return []

    sentences = [s.strip() for s in SENTENCE_SPLIT_RE.split(text) if s.strip()]
    sentences = [s for s in sentences if len(s) >= min_length]
    if not sentences:
        return []

    word_freq = Counter()
    sentence_words = []
    for sentence in sentences:
        words = {w for w in WORD_RE.findall(sentence) if w not in STOPWORDS}
        sentence_words.append(words)
        for w in words:
            word_freq[w] += 1

    def score(words: set) -> float:
        if not words:
            return 0.0
        return sum(word_freq.get(w, 0) for w in words) / len(words)

    ranked = sorted(range(len(sentences)), key=lambda i: score(sentence_words[i]), reverse=True)

    selected_idx = []
    covered_words = set()
    for i in ranked:
        words = sentence_words[i]
        overlap = len(words & covered_words) / len(words) if words else 0
        if overlap > 0.6 and selected_idx:
            continue  # 既に選んだ要点と内容が被りすぎる場合はスキップ
        selected_idx.append(i)
        covered_words |= words
        if len(selected_idx) >= max_points:
            break

    if not selected_idx:
        selected_idx = ranked[:max_points]

    selected_idx = sorted(selected_idx)
    return [sentences[i].rstrip("。.!?！？") + "。" for i in selected_idx]


def summarize_by_topic(
    video_info: Dict,
    segments: Optional[List[Dict]],
    points_per_topic: int = 4,
) -> List[Dict]:
    """トピックごとに区間を切り出し、箇条書きの要点を付与したリストを返す"""
    topics = build_topics(video_info, segments)

    result = []
    for topic in topics:
        start, end = topic["start"], topic["end"]
        seg_texts = [
            (seg.get("text") or "").strip()
            for seg in (segments or [])
            if start <= seg.get("start", 0) < end and (seg.get("text") or "").strip()
        ]
        topic_text = "".join(seg_texts)
        points = extract_key_points(topic_text, max_points=points_per_topic)

        result.append({
            "title": topic["title"],
            "start": start,
            "end": end,
            "points": points or ["（この区間のトランスクリプトを取得できませんでした）"],
        })

    logger.info(f"Generated {len(result)} topic summaries")
    return result
