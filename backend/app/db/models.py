"""
数据库模型定义
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Article(Base):
    """文章模型"""
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=False)  # 标题
    category = Column(String(50), nullable=False)  # 分类：llm/industry/politics/finance
    url = Column(Text, unique=True, nullable=False)  # 原文链接
    source = Column(String(200))  # 来源网站
    author = Column(String(200))  # 作者
    published_at = Column(DateTime)  # 发布时间
    summary = Column(Text)  # 摘要（150-200 字）
    content = Column(Text)  # 净化后的正文
    image_urls = Column(Text)  # JSON 数组，最多 5 张图片
    fetched_at = Column(DateTime, default=datetime.utcnow)  # 抓取时间
    is_processed = Column(Boolean, default=False)  # 是否已处理

    def to_dict(self):
        """转换为字典"""
        import json
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "url": self.url,
            "source": self.source,
            "author": self.author,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "summary": self.summary,
            "content": self.content,
            "image_urls": json.loads(self.image_urls) if self.image_urls else [],
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
            "is_processed": self.is_processed,
        }


def init_db(database_url: str):
    """初始化数据库"""
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal, engine
