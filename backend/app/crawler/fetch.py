"""
原文抓取模块
抓取并解析文章原文
"""
import re
import requests
from bs4 import BeautifulSoup
from typing import Optional, List
from urllib.parse import urljoin, urlparse


class ArticleFetcher:
    """文章抓取器"""

    # 常见广告容器选择器
    AD_SELECTORS = [
        ".ad", ".ads", ".advertisement", ".advert",
        "[class*='sponsor']", "[id*='sponsor']",
        ".promo", ".promotion", ".banner",
        "#popup", ".popup", ".modal-ad",
        ".sidebar-ad", ".right-ad", ".bottom-ad",
        "[class*='ad-container']", "[class*='ad-wrapper']",
    ]

    # 需要移除的标签
    REMOVE_TAGS = ["script", "style", "iframe", "noscript", "form", "nav", "footer", "header"]

    # 广告关键词
    AD_KEYWORDS = ["广告", "sponsor", "promo", "advertisement", "推广", "合作"]

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })

    def fetch(self, url: str) -> Optional[dict]:
        """
        抓取文章

        Args:
            url: 文章 URL

        Returns:
            解析后的文章数据
        """
        try:
            print(f"[Fetch] 抓取：{url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            html = response.text
            soup = BeautifulSoup(html, "lxml")

            # 提取元数据
            metadata = self._extract_metadata(soup, url)

            # 移除广告和不需要的元素
            self._remove_ads(soup)

            # 提取正文
            content = self._extract_content(soup)

            # 提取图片
            images = self._extract_images(soup, url)

            # 清理内容
            content = self._clean_content(content)

            return {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "published_at": metadata.get("published_at"),
                "content": content,
                "image_urls": images[:5],  # 最多 5 张
                "source": metadata.get("source", ""),
            }

        except Exception as e:
            print(f"[Fetch] 抓取失败：{e}")
            return None

    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> dict:
        """提取元数据"""
        metadata = {}

        # 标题
        title = soup.find("title")
        metadata["title"] = title.get_text(strip=True) if title else ""

        # OG 标签
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            metadata["title"] = og_title["content"]

        # 作者
        author = soup.find("meta", attrs={"name": "author"})
        metadata["author"] = author.get("content") if author and author.get("content") else ""

        # 发布时间
        published_time = soup.find("meta", attrs={"property": "article:published_time"})
        if published_time and published_time.get("content"):
            from datetime import datetime
            try:
                metadata["published_at"] = datetime.fromisoformat(
                    published_time["content"].replace("Z", "+00:00")
                )
            except:
                pass

        # 来源
        parsed = urlparse(url)
        metadata["source"] = parsed.netloc.replace("www.", "")

        return metadata

    def _remove_ads(self, soup: BeautifulSoup):
        """移除广告元素"""
        # 移除不需要的标签
        for tag_name in self.REMOVE_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        # 移除广告容器
        for selector in self.AD_SELECTORS:
            try:
                for tag in soup.select(selector):
                    tag.decompose()
            except:
                pass

        # 移除包含广告关键词的段落
        for p in soup.find_all("p"):
            text = p.get_text().lower()
            if any(keyword.lower() in text for keyword in self.AD_KEYWORDS):
                p.decompose()

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """提取正文内容"""
        # 尝试查找 article 标签
        article = soup.find("article")
        if article:
            return self._html_to_markdown(article)

        # 尝试查找 main 标签
        main = soup.find("main")
        if main:
            return self._html_to_markdown(main)

        # 尝试查找 content 类
        content = soup.find(class_=re.compile(r"content|article|post|entry", re.I))
        if content:
            return self._html_to_markdown(content)

        # 退而求其次，提取所有段落
        paragraphs = soup.find_all("p")
        content_parts = []
        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 50:  # 过滤太短的段落
                content_parts.append(text)

        return "\n\n".join(content_parts)

    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> list[str]:
        """提取图片"""
        images = []

        # OG Image
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            images.append(og_image["content"])

        # Article Image
        article_image = soup.find("meta", attrs={"property": "article:image"})
        if article_image and article_image.get("content"):
            images.append(article_image["content"])

        # 正文中的图片
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src")
            if src:
                # 转为绝对路径
                full_url = urljoin(base_url, src)
                images.append(full_url)

        # 去重
        seen = set()
        unique_images = []
        for img in images:
            if img and img not in seen:
                unique_images.append(img)
                seen.add(img)

        return unique_images

    def _html_to_markdown(self, element) -> str:
        """简单的 HTML 转 Markdown"""
        if not element:
            return ""

        # 获取纯文本
        text = element.get_text(separator="\n\n", strip=True)

        # 清理多余空行
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text

    def _clean_content(self, content: str) -> str:
        """清理内容"""
        # 移除多余空白
        content = re.sub(r"\s+", " ", content)
        # 移除多余空行
        content = re.sub(r"\n{3,}", "\n\n", content)
        return content.strip()


if __name__ == "__main__":
    # 测试抓取
    fetcher = ArticleFetcher()
    result = fetcher.fetch("https://example.com/article")
    if result:
        print(f"标题：{result['title']}")
        print(f"内容长度：{len(result['content'])}")
