"""
内容清洗模块
广告过滤、内容标准化
"""
import re
from typing import Optional, List


class ContentCleaner:
    """内容清洗器"""

    # 广告关键词（中英文）
    AD_PATTERNS = [
        r"广告", r"推广", r"赞助", r"合作",
        r"advertising", r"sponsor", r"promo", r"advertisement",
        r"点击.*?购买", r"立即.*?注册", r"限时.*?优惠",
    ]

    # 需要保留的 HTML 标签（如果要保留部分格式）
    ALLOWED_TAGS = ["p", "br", "strong", "em", "ul", "ol", "li", "h1", "h2", "h3", "h4", "h5", "h6"]

    def __init__(self):
        self.ad_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.AD_PATTERNS]

    def clean(self, content: str) -> tuple:
        """
        清洗内容

        Args:
            content: 原始内容

        Returns:
            (清洗后的内容，摘要) 元组
        """
        if not content:
            return "", None

        # 1. 移除广告段落
        content = self._remove_ads(content)

        # 2. 标准化空白
        content = self._normalize_whitespace(content)

        # 3. 生成摘要
        summary = self._generate_summary(content)

        return content, summary

    def _remove_ads(self, content: str) -> str:
        """移除广告内容"""
        lines = content.split("\n")
        clean_lines = []

        for line in lines:
            # 检查是否包含广告关键词
            is_ad = any(pattern.search(line) for pattern in self.ad_regex)
            if not is_ad and line.strip():
                clean_lines.append(line)

        return "\n".join(clean_lines)

    def _normalize_whitespace(self, content: str) -> str:
        """标准化空白"""
        # 移除多余空格
        content = re.sub(r" +", " ", content)
        # 移除多余空行
        content = re.sub(r"\n{3,}", "\n\n", content)
        # 移除行首行尾空白
        content = content.strip()
        return content

    def _generate_summary(self, content: str, max_length: int = 200) -> Optional[str]:
        """
        生成摘要

        Args:
            content: 内容
            max_length: 最大长度

        Returns:
            摘要
        """
        if not content:
            return None

        # 取第一段作为摘要
        paragraphs = content.split("\n\n")
        if paragraphs:
            summary = paragraphs[0].strip()
            if len(summary) > max_length:
                summary = summary[:max_length - 3] + "..."
            return summary

        return None

    def extract_keywords(self, content: str, max_keywords: int = 5) -> list[str]:
        """
        提取关键词（简单版）

        Args:
            content: 内容
            max_keywords: 最大关键词数

        Returns:
            关键词列表
        """
        # 简单实现：取出现频率最高的词
        # 实际项目中可以用 jieba 或 TF-IDF
        words = re.findall(r"[\w]+", content.lower())

        # 过滤常见停用词
        stopwords = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being"}
        words = [w for w in words if w not in stopwords and len(w) > 3]

        # 计数
        from collections import Counter
        word_counts = Counter(words)

        return [word for word, _ in word_counts.most_common(max_keywords)]


if __name__ == "__main__":
    # 测试清洗
    cleaner = ContentCleaner()
    test_content = """
    这是一篇好文章。

    广告：点击购买我们的产品！

    这是正文内容，非常重要。

    赞助内容：某品牌赞助了我们。

    继续正文...
    """
    cleaned, summary = cleaner.clean(test_content)
    print(f"清洗后:\n{cleaned}")
    print(f"\n摘要：{summary}")
