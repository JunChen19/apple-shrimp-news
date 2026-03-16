"""
数据库连接管理
"""
import os
from typing import Optional, List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from .models import Base, Article

# 从环境变量读取数据库 URL（使用同步 sqlite3）
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/articles.db")

# 创建引擎（SQLite 不需要连接池）
engine = create_engine(DATABASE_URL, echo=False)

# Session 工厂
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db():
    """初始化数据库表"""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db() -> Session:
    """获取数据库会话（上下文管理器）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_article_by_url(db: Session, url: str) -> Optional[Article]:
    """根据 URL 查询文章（用于去重）"""
    return db.query(Article).filter(Article.url == url).first()


def create_article(db: Session, article_data: dict) -> Article:
    """创建新文章"""
    article = Article(**article_data)
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def get_articles(db: Session, category: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Article]:
    """获取文章列表"""
    query = db.query(Article).filter(Article.is_processed == True)
    if category:
        query = query.filter(Article.category == category)
    return query.order_by(Article.published_at.desc()).offset(offset).limit(limit).all()


def get_article_by_id(db: Session, article_id: int) -> Optional[Article]:
    """根据 ID 获取文章"""
    return db.query(Article).filter(Article.id == article_id).first()


def update_article(db: Session, article_id: int, update_data: dict) -> Optional[Article]:
    """更新文章"""
    article = db.query(Article).filter(Article.id == article_id).first()
    if article:
        for key, value in update_data.items():
            setattr(article, key, value)
        db.commit()
        db.refresh(article)
    return article
