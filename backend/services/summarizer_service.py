from anthropic import Anthropic
import logging
from typing import Optional
from config import settings

logger = logging.getLogger(__name__)


class SummarizerService:
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def summarize_transcript(self, transcript: str) -> Optional[str]:
        """トランスクリプトをサマライズ"""
        try:
            if not transcript:
                logger.warning("Empty transcript provided")
                return None

            message = self.client.messages.create(
                model=settings.SUMMARY_MODEL,
                max_tokens=settings.SUMMARY_MAX_TOKENS,
                messages=[
                    {
                        "role": "user",
                        "content": f"""以下のYouTube動画のトランスクリプトを、分かりやすく日本語で要約してください。

要約のポイント:
- 主なトピックを箇条書きで記載
- 重要な発見や結論をハイライト
- わかりやすく、簡潔に
- 適切なセクションに分ける

トランスクリプト:
{transcript}

要約:""",
                    }
                ],
            )

            summary = message.content[0].text
            logger.info(f"Summary generated: {len(summary)} chars")
            return summary

        except Exception as e:
            logger.error(f"Failed to summarize: {str(e)}")
            return None

    async def generate_detailed_report(
        self,
        title: str,
        description: str,
        transcript: str,
        duration: float,
    ) -> Optional[str]:
        """詳細レポートを生成"""
        try:
            prompt = f"""以下の動画情報に基づいて、詳細で構造化されたレポートを生成してください。

動画タイトル: {title}
説明: {description}
長さ: {int(duration)}秒

トランスクリプト:
{transcript}

以下のセクションを含む詳細レポートを作成してください:
1. 概要 - 動画の全体的な内容
2. 主な要点 - 重要なポイント（箇条書き）
3. キーテイクアウェイ - 視聴者が得られる知見
4. 詳細分析 - より深い考察
5. 行動可能な次のステップ

レポート:"""

            message = self.client.messages.create(
                model=settings.SUMMARY_MODEL,
                max_tokens=settings.SUMMARY_MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}],
            )

            report = message.content[0].text
            logger.info(f"Detailed report generated: {len(report)} chars")
            return report

        except Exception as e:
            logger.error(f"Failed to generate report: {str(e)}")
            return None
