import logging
from datetime import datetime
from typing import Optional, List

logger = logging.getLogger(__name__)


class ReportGenerator:
    @staticmethod
    def generate_html_report(
        title: str,
        description: str,
        duration: float,
        summary: str,
        screenshots: list,
        detailed_report: Optional[str] = None,
        topics: Optional[List[dict]] = None,
    ) -> str:
        """HTMLレポートを生成（テキスト + スクリーンショット並行表示）"""

        def format_duration(seconds: float) -> str:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            if hours > 0:
                return f"{hours}時間 {minutes}分 {secs}秒"
            return f"{minutes}分 {secs}秒"

        def format_time(seconds: float) -> str:
            seconds = int(seconds or 0)
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            if hours > 0:
                return f"{hours}:{minutes:02d}:{secs:02d}"
            return f"{minutes}:{secs:02d}"

        def escape_html(text: str) -> str:
            """HTML特殊文字をエスケープ"""
            return (
                text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&#39;")
            )

        def truncate_description(text: str, max_chars: int = 300) -> str:
            """動画説明欄が長すぎる場合に短縮（最初の段落を優先）"""
            text = (text or "").strip()
            if not text:
                return ""
            first_paragraph = text.split("\n\n")[0].strip()
            candidate = first_paragraph if first_paragraph else text
            if len(candidate) <= max_chars:
                return candidate
            return candidate[:max_chars].rstrip() + "…"

        summary_html = ""

        if topics:
            # トピックごとのサマリー（箇条書き） + スクリーンショット
            for topic in topics:
                topic_title = escape_html(topic.get("title", ""))
                time_label = format_time(topic.get("start", 0))
                points = topic.get("points") or (
                    [topic["summary"]] if topic.get("summary") else []
                )
                points_html = "".join(
                    f"<li>{escape_html(point)}</li>" for point in points
                )
                img = topic.get("image")
                image_html = (
                    f'<div class="image-section"><img src="{img}" alt="{topic_title}" /></div>'
                    if img else '<div class="image-section empty"></div>'
                )

                summary_html += f"""
                <div class="content-block">
                    <div class="text-section">
                        <h3 class="topic-title">{topic_title} <span class="time-badge">{time_label}</span></h3>
                        <div class="text-content">
                            <ul class="summary-points">
                                {points_html}
                            </ul>
                        </div>
                    </div>
                    {image_html}
                </div>
                """
        else:
            # 後方互換: サマリーを段落ごとに分割
            summary_blocks = [block.strip() for block in summary.split('\n\n') if block.strip()]

            for i, block in enumerate(summary_blocks):
                screenshot = screenshots[i] if i < len(screenshots) else None

                summary_html += f"""
                <div class="content-block">
                    <div class="text-section">
                        <div class="text-content">
                            {escape_html(block).replace(chr(10), '<br>')}
                        </div>
                    </div>
                    {f'<div class="image-section"><img src="{screenshot}" alt="Screenshot {i+1}" /></div>' if screenshot else '<div class="image-section empty"></div>'}
                </div>
                """

        # 詳細レポート（オプション）
        detailed_html = ""
        if detailed_report:
            detailed_blocks = [block.strip() for block in detailed_report.split('\n\n') if block.strip()]
            for i, block in enumerate(detailed_blocks):
                screenshot_idx = len(summary_blocks) + i
                screenshot = screenshots[screenshot_idx] if screenshot_idx < len(screenshots) else None

                detailed_html += f"""
                <div class="content-block">
                    <div class="text-section">
                        <div class="text-content">
                            {escape_html(block).replace(chr(10), '<br>')}
                        </div>
                    </div>
                    {f'<div class="image-section"><img src="{screenshot}" alt="Screenshot" /></div>' if screenshot else '<div class="image-section empty"></div>'}
                </div>
                """

            if detailed_html:
                detailed_html = f"""
                <div class="section">
                    <h2>詳細レポート</h2>
                    {detailed_html}
                </div>
                """

        current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")

        html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape_html(title)} - YouTube Video Summary</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        html, body {{
            height: 100%;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
                'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 50px 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.8em;
            margin-bottom: 15px;
            word-break: break-word;
            font-weight: 700;
        }}

        .header-meta {{
            font-size: 0.95em;
            opacity: 0.95;
            margin-top: 20px;
        }}

        .header-meta p {{
            margin: 8px 0;
        }}

        .content {{
            padding: 50px 40px;
        }}

        .section {{
            margin-bottom: 60px;
        }}

        .section:last-child {{
            margin-bottom: 0;
        }}

        .section h2 {{
            font-size: 2em;
            color: #667eea;
            margin-bottom: 35px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
            font-weight: 700;
        }}

        .intro-section {{
            background: #f8f9fa;
            padding: 30px;
            border-left: 5px solid #667eea;
            border-radius: 8px;
            margin-bottom: 40px;
            font-size: 0.98em;
            line-height: 1.9;
        }}

        .content-block {{
            display: grid;
            grid-template-columns: 1.2fr 1fr;
            gap: 40px;
            margin-bottom: 50px;
            align-items: start;
        }}

        .text-section {{
            flex: 1;
        }}

        .topic-title {{
            font-size: 1.25em;
            color: #444;
            margin-bottom: 15px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .time-badge {{
            display: inline-block;
            background: #e9e4fb;
            color: #667eea;
            padding: 3px 10px;
            border-radius: 14px;
            font-size: 0.7em;
            font-weight: 600;
        }}

        .text-content {{
            background: #f8f9fa;
            padding: 30px;
            border-left: 5px solid #667eea;
            border-radius: 8px;
            line-height: 1.9;
            font-size: 0.97em;
            color: #444;
        }}

        .text-content br {{
            margin: 8px 0;
        }}

        .summary-points {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}

        .summary-points li {{
            position: relative;
            padding-left: 22px;
            margin-bottom: 12px;
        }}

        .summary-points li:last-child {{
            margin-bottom: 0;
        }}

        .summary-points li::before {{
            content: "";
            position: absolute;
            left: 0;
            top: 0.65em;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #667eea;
        }}

        .image-section {{
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
            background: #e9ecef;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 320px;
            max-height: 420px;
        }}

        .image-section img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }}

        .image-section.empty {{
            border: 2px dashed #d0d0d0;
            color: #999;
            font-size: 14px;
        }}

        .footer {{
            background: #f8f9fa;
            padding: 30px 40px;
            text-align: center;
            font-size: 0.85em;
            color: #777;
            border-top: 1px solid #e9ecef;
        }}

        .duration-badge {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 8px 16px;
            border-radius: 24px;
            font-size: 0.95em;
            font-weight: 600;
            margin-left: 12px;
        }}

        @media print {{
            body {{
                background: white;
                padding: 0;
            }}

            .container {{
                box-shadow: none;
                border-radius: 0;
            }}

            .content-block {{
                page-break-inside: avoid;
            }}
        }}

        @media (max-width: 1024px) {{
            .content-block {{
                grid-template-columns: 1fr;
                gap: 25px;
            }}

            .image-section {{
                min-height: 250px;
            }}

            .header {{
                padding: 40px 30px;
            }}

            .header h1 {{
                font-size: 2em;
            }}

            .content {{
                padding: 35px 25px;
            }}
        }}

        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8em;
            }}

            .content {{
                padding: 25px 20px;
            }}

            .section h2 {{
                font-size: 1.5em;
            }}

            .text-content {{
                padding: 20px;
                font-size: 0.95em;
            }}

            .image-section {{
                min-height: 200px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{escape_html(title)}</h1>
            <div class="header-meta">
                <p>動画の長さ: <span class="duration-badge">{format_duration(duration)}</span></p>
                <p style="margin-top: 15px; font-size: 0.9em;">生成日時: {current_time}</p>
            </div>
        </div>

        <div class="content">
            <!-- 動画説明 -->
            <div class="section">
                <h2>概要</h2>
                {f'<div class="intro-section">{escape_html(truncate_description(description))}</div>' if description else ''}
            </div>

            <!-- サマリー -->
            <div class="section">
                <h2>サマリー</h2>
                {summary_html}
            </div>

            <!-- 詳細レポート -->
            {detailed_html}
        </div>

        <div class="footer">
            <p>このレポートはYouTube Video Summarizerで自動生成されました</p>
        </div>
    </div>
</body>
</html>"""

        return html_content
