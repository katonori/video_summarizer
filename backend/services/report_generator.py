import logging
from datetime import datetime
from typing import Optional

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
    ) -> str:
        """HTMLレポートを生成"""

        def format_duration(seconds: float) -> str:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            if hours > 0:
                return f"{hours}時間 {minutes}分 {secs}秒"
            return f"{minutes}分 {secs}秒"

        def escape_html(text: str) -> str:
            """HTML特殊文字をエスケープ"""
            return (
                text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&#39;")
            )

        screenshots_html = ""
        if screenshots:
            screenshots_html = "<div class='screenshots-section'>"
            screenshots_html += "<h2>ビデオスクリーンショット</h2>"
            screenshots_html += "<div class='screenshot-grid'>"
            for i, screenshot in enumerate(screenshots, 1):
                screenshots_html += f"""
                <div class='screenshot-item'>
                    <img src="{screenshot}" alt="Screenshot {i}" />
                </div>
                """
            screenshots_html += "</div></div>"

        detailed_report_html = ""
        if detailed_report:
            detailed_report_html = f"""
            <div class='detailed-report-section'>
                <h2>詳細レポート</h2>
                <div class='report-content'>
                    {escape_html(detailed_report).replace(chr(10), '<br>')}
                </div>
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
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            word-break: break-word;
        }}

        .header-meta {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-top: 15px;
        }}

        .header-meta p {{
            margin: 5px 0;
        }}

        .content {{
            padding: 40px 30px;
        }}

        .section {{
            margin-bottom: 40px;
        }}

        .section h2 {{
            font-size: 1.8em;
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}

        .description {{
            background: #f8f9fa;
            padding: 20px;
            border-left: 4px solid #667eea;
            border-radius: 4px;
            margin-bottom: 30px;
            font-size: 0.95em;
            line-height: 1.8;
        }}

        .summary-content {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 8px;
            line-height: 1.8;
            font-size: 0.95em;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}

        .screenshots-section {{
            margin-top: 30px;
        }}

        .screenshot-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        .screenshot-item {{
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}

        .screenshot-item:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        }}

        .screenshot-item img {{
            width: 100%;
            height: auto;
            display: block;
            background: #e9ecef;
        }}

        .detailed-report-section {{
            margin-top: 40px;
            background: #f8f9fa;
            padding: 25px;
            border-radius: 8px;
        }}

        .report-content {{
            line-height: 1.8;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-size: 0.95em;
        }}

        .footer {{
            background: #f8f9fa;
            padding: 20px 30px;
            text-align: center;
            font-size: 0.85em;
            color: #666;
            border-top: 1px solid #e9ecef;
        }}

        .duration-badge {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-left: 10px;
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

            .screenshot-item {{
                break-inside: avoid;
            }}
        }}

        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8em;
            }}

            .content {{
                padding: 20px;
            }}

            .screenshot-grid {{
                grid-template-columns: 1fr;
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
                <p style="margin-top: 10px; font-size: 0.85em;">生成日時: {current_time}</p>
            </div>
        </div>

        <div class="content">
            <div class="section">
                <h2>動画について</h2>
                {f'<div class="description">{escape_html(description)}</div>' if description else '<p style="color: #999;">説明はありません</p>'}
            </div>

            <div class="section">
                <h2>サマリー</h2>
                <div class="summary-content">{escape_html(summary)}</div>
            </div>

            {screenshots_html}

            {detailed_report_html}
        </div>

        <div class="footer">
            <p>このレポートはYouTube Video Summarizerで自動生成されました</p>
        </div>
    </div>
</body>
</html>"""

        return html_content
