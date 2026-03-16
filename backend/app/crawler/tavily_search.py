"""
Tavily 搜索模块
四大板块的定向搜索策略
"""
import os
import json
from datetime import datetime
from typing import Optional, List
from tavily import TavilyClient

# 搜索策略配置
SEARCH_QUERIES = {
    "llm": "GPT Claude Llama large language model update release 2026",
    "industry": "AI startup funding acquisition product launch news 2026",
    "politics": "AI technology policy regulation international government 2026",
    "finance": "tech stock AI concept stock financing valuation 2026",
}

SEARCH_CONFIG = {
    "search_depth": "advanced",  # advanced 或 basic
    "max_results": 15,  # 每个板块最多 15 条
    "include_answer": True,
    "include_raw_content": False,
}


class TavilySearcher:
    """Tavily 搜索器"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY is required")
        self.client = TavilyClient(api_key=self.api_key)

    def search_category(self, category: str) -> list[dict]:
        """
        搜索指定板块的资讯

        Args:
            category: 板块名称 (llm/industry/politics/finance)

        Returns:
            搜索结果列表
        """
        query = SEARCH_QUERIES.get(category)
        if not query:
            raise ValueError(f"Unknown category: {category}")

        print(f"[Tavily] 搜索 {category}: {query}")

        try:
            response = self.client.search(
                query=query,
                search_depth=SEARCH_CONFIG["search_depth"],
                max_results=SEARCH_CONFIG["max_results"],
                include_answer=SEARCH_CONFIG["include_answer"],
            )

            results = []
            for result in response.get("results", []):
                # 去重检查（基于 URL）
                article = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "source": self._extract_source(result.get("url", "")),
                    "summary": result.get("content", "")[:300],  # 摘要截取 300 字
                    "published_at": self._parse_published_at(result),
                    "category": category,
                    "raw_content": result.get("content", ""),
                }
                results.append(article)

            print(f"[Tavily] {category} 找到 {len(results)} 条结果")
            return results

        except Exception as e:
            print(f"[Tavily] 搜索失败：{e}")
            return []

    def search_all_categories(self) -> dict[str, list[dict]]:
        """搜索所有板块"""
        results = {}
        for category in SEARCH_QUERIES.keys():
            results[category] = self.search_category(category)
        return results

    def _extract_source(self, url: str) -> str:
        """从 URL 提取来源网站"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "")
        return domain.split(".")[0].title()

    def _parse_published_at(self, result: dict) -> Optional[datetime]:
        """解析发布时间（Tavily 不直接提供，用当前时间替代）"""
        # 后续可以通过抓取原文获取更准确的发布时间
        return datetime.utcnow()


def deduplicate_articles(articles: list[dict], existing_urls: set[str]) -> list[dict]:
    """
    去重文章

    Args:
        articles: 新抓取的文章列表
        existing_urls: 已存在的 URL 集合

    Returns:
        去重后的文章列表
    """
    seen_urls = set()
    unique_articles = []

    for article in articles:
        url = article.get("url", "")
        if url and url not in existing_urls and url not in seen_urls:
            unique_articles.append(article)
            seen_urls.add(url)

    print(f"[去重] 过滤后剩余 {len(unique_articles)} 条新文章")
    return unique_articles


if __name__ == "__main__":
    # 测试搜索
    searcher = TavilySearcher()
    results = searcher.search_category("llm")
    print(json.dumps(results[:2], indent=2, ensure_ascii=False))
