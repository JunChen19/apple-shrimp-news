"""
图片处理模块
下载并缓存文章图片
"""
import os
import uuid
import requests
from pathlib import Path
from typing import Optional, List
from urllib.parse import urlparse


class ImageProcessor:
    """图片处理器"""

    def __init__(self, output_dir: str = "public/images"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        })

    def download_images(self, image_urls: list[str], article_id: int) -> list[str]:
        """
        下载图片到本地

        Args:
            image_urls: 图片 URL 列表
            article_id: 文章 ID（用于组织目录）

        Returns:
            本地图片路径列表
        """
        if not image_urls:
            return []

        # 为每篇文章创建子目录
        article_dir = self.output_dir / str(article_id)
        article_dir.mkdir(parents=True, exist_ok=True)

        local_paths = []

        for i, url in enumerate(image_urls[:5]):  # 最多 5 张
            try:
                local_path = self._download_single(url, article_dir, i)
                if local_path:
                    local_paths.append(local_path)
            except Exception as e:
                print(f"[Image] 下载失败 {url}: {e}")

        return local_paths

    def _download_single(self, url: str, article_dir: Path, index: int) -> Optional[str]:
        """下载单张图片"""
        try:
            # 生成文件名
            ext = self._get_extension(url)
            filename = f"{index:02d}_{uuid.uuid4().hex[:8]}.{ext}"
            local_path = article_dir / filename

            # 下载
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # 检查分辨率（可选）
            # 这里简化处理，直接保存

            # 保存
            with open(local_path, "wb") as f:
                f.write(response.content)

            print(f"[Image] 已下载：{local_path}")
            return str(local_path)

        except Exception as e:
            print(f"[Image] 下载失败：{e}")
            return None

    def _get_extension(self, url: str) -> str:
        """从 URL 获取文件扩展名"""
        parsed = urlparse(url)
        path = parsed.path.lower()

        if path.endswith(".png"):
            return "png"
        elif path.endswith(".gif"):
            return "gif"
        elif path.endswith(".webp"):
            return "webp"
        elif path.endswith(".svg"):
            return "svg"
        else:
            return "jpg"  # 默认

    def get_relative_path(self, local_path: str) -> str:
        """获取相对路径（用于前端访问）"""
        return os.path.relpath(local_path, self.output_dir.parent.parent)


if __name__ == "__main__":
    # 测试下载
    processor = ImageProcessor()
    urls = [
        "https://example.com/image1.jpg",
        "https://example.com/image2.png",
    ]
    paths = processor.download_images(urls, article_id=1)
    print(f"下载到：{paths}")
