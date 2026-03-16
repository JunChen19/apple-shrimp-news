#!/usr/bin/env python3
"""
导出静态页面到 GitHub Pages
"""
import os
import json
import shutil
from pathlib import Path
from datetime import datetime

import requests

# 配置
API_URL = os.getenv("NEXT_PUBLIC_API_URL", "http://localhost:8000")
OUTPUT_DIR = Path("frontend/out")
DATA_DIR = Path("backend/data")


def fetch_articles():
    """从 API 获取所有文章"""
    print("获取文章列表...")
    response = requests.get(f"{API_URL}/api/articles?limit=1000")
    response.raise_for_status()
    return response.json()


def generate_index_html(articles: list[dict]) -> str:
    """生成首页 HTML"""
    categories = {
        "llm": "🤖 大模型动态",
        "industry": "📰 AI 行业资讯",
        "politics": "🌍 国际政治",
        "finance": "💰 金融板块",
    }

    # 按分类分组
    grouped = {cat: [] for cat in categories}
    for article in articles:
        cat = article.get("category", "llm")
        if cat in grouped:
            grouped[cat].append(article)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>苹果虾资讯 - AI 资讯聚合平台</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        header {{ background: white; padding: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        header h1 {{ text-align: center; color: #333; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 30px; }}
        .card {{ background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .card h2 {{ color: #333; margin-bottom: 15px; font-size: 1.5em; }}
        .article {{ border-bottom: 1px solid #eee; padding: 15px 0; }}
        .article:last-child {{ border-bottom: none; }}
        .article h3 {{ color: #0066cc; margin-bottom: 8px; }}
        .article h3 a {{ text-decoration: none; }}
        .article h3 a:hover {{ text-decoration: underline; }}
        .meta {{ font-size: 0.85em; color: #666; }}
        .summary {{ color: #555; margin-top: 8px; line-height: 1.5; }}
        footer {{ text-align: center; padding: 30px 0; color: #666; }}
        @media (max-width: 768px) {{
            .grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>🦐 苹果虾资讯</h1>
            <p style="text-align: center; color: #666; margin-top: 10px;">AI 资讯聚合平台 - 每日更新</p>
        </div>
    </header>

    <main class="container">
        <div class="grid">
"""

    for cat, label in categories.items():
        cat_articles = grouped[cat][:10]  # 每个板块最多 10 篇
        html += f"""
            <div class="card">
                <h2>{label}</h2>
"""
        for article in cat_articles:
            html += f"""
                <div class="article">
                    <h3><a href="article_{article['id']}.html">{article['title']}</a></h3>
                    <div class="meta">
                        <span>{article.get('source', '未知')}</span>
                        <span> • </span>
                        <span>{article.get('published_at', '')[:10] if article.get('published_at') else '未知'}</span>
                    </div>
                    <p class="summary">{article.get('summary', '')[:100]}...</p>
                </div>
"""
        html += """
            </div>
"""

    html += f"""
        </div>
    </main>

    <footer>
        <div class="container">
            <p>最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            <p>数据来源：Tavily API</p>
        </div>
    </footer>
</body>
</html>
"""
    return html


def generate_article_html(article: dict) -> str:
    """生成文章详情页 HTML"""
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article['title']} - 苹果虾资讯</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        header {{ background: white; padding: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        header a {{ text-decoration: none; color: #333; }}
        article {{ background: white; padding: 40px; margin-top: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; margin-bottom: 20px; line-height: 1.3; }}
        .meta {{ color: #666; font-size: 0.9em; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #eee; }}
        .content {{ color: #333; line-height: 1.8; }}
        .content p {{ margin-bottom: 20px; }}
        .original-btn {{ display: inline-block; background: #0066cc; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; margin-top: 30px; }}
        .original-btn:hover {{ background: #0055aa; }}
        .back-link {{ display: inline-block; margin-bottom: 20px; color: #0066cc; text-decoration: none; }}
        .back-link:hover {{ text-decoration: underline; }}
        footer {{ text-align: center; padding: 30px 0; color: #666; }}
        @media (max-width: 768px) {{
            article {{ padding: 20px; }}
            h1 {{ font-size: 1.5em; }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <a href="index.html">🦐 苹果虾资讯</a>
        </div>
    </header>

    <main class="container">
        <a href="index.html" class="back-link">← 返回首页</a>

        <article>
            <h1>{article['title']}</h1>
            <div class="meta">
                <span>来源：{article.get('source', '未知')}</span>
                <span> • </span>
                <span>分类：{article.get('category', '未知')}</span>
                <span> • </span>
                <span>发布时间：{article.get('published_at', '')[:10] if article.get('published_at') else '未知'}</span>
            </div>

            <div class="content">
                <p><strong>摘要：</strong>{article.get('summary', '无摘要')}</p>
                <p style="margin-top: 30px;">
                    <a href="{article['url']}" target="_blank" rel="noopener" class="original-btn">
                        📄 查看原文
                    </a>
                </p>
            </div>
        </article>
    </main>

    <footer>
        <div class="container">
            <p><a href="{article['url']}" target="_blank" rel="noopener">原文链接</a></p>
        </div>
    </footer>
</body>
</html>
"""
    return html


def main():
    """主函数"""
    print("开始导出静态页面...")

    # 创建输出目录
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 获取文章
    articles = fetch_articles()
    print(f"获取到 {len(articles)} 篇文章")

    # 生成首页
    index_html = generate_index_html(articles)
    with open(OUTPUT_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
    print("✅ 首页生成完成")

    # 生成文章页
    for article in articles:
        article_html = generate_article_html(article)
        with open(OUTPUT_DIR / f"article_{article['id']}.html", "w", encoding="utf-8") as f:
            f.write(article_html)

    print(f"✅ 生成 {len(articles)} 篇文章页面")
    print(f"\n输出目录：{OUTPUT_DIR.absolute()}")
    print("部署命令：gh-pages -d frontend/out")


if __name__ == "__main__":
    main()
