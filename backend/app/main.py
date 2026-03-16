"""
FastAPI 主应用
"""
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .db.database import init_db, get_db, get_articles, get_article_by_id, get_article_by_url, create_article, update_article
from .db.models import Article
from .crawler.tavily_search import TavilySearcher, deduplicate_articles
from .crawler.fetch import ArticleFetcher
from .crawler.images import ImageProcessor
from .crawler.clean import ContentCleaner

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="苹果虾资讯 API",
    description="AI 资讯聚合平台后端接口",
    version="1.0.0",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化组件
image_processor = ImageProcessor(output_dir="public/images")
content_cleaner = ContentCleaner()
article_fetcher = ArticleFetcher()

# 确保数据目录存在
Path("data").mkdir(parents=True, exist_ok=True)
Path("logs").mkdir(parents=True, exist_ok=True)
Path("public/images").mkdir(parents=True, exist_ok=True)


# ==================== 数据模型 ====================


class ArticleResponse(BaseModel):
    """文章响应"""

    id: int
    title: str
    category: str
    url: str
    source: str
    author: Optional[str] = None
    published_at: Optional[str] = None
    summary: Optional[str] = None
    image_urls: list = []
    fetched_at: Optional[str] = None


class FetchRequest(BaseModel):
    """手动触发抓取请求"""

    categories: Optional[list[str]] = None  # 指定板块，不传则全部


class HealthResponse(BaseModel):
    """健康检查响应"""

    status: str
    database: str
    tavily: str
    last_update: Optional[str] = None


# ==================== API 接口 ====================


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "苹果虾资讯 API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    db_status = "ok"
    tavily_status = "ok"
    last_update = None

    try:
        with get_db() as db:
            # 检查数据库
            latest = get_articles(db, limit=1)
            if latest:
                last_update = latest[0].fetched_at.isoformat()
    except Exception as e:
        db_status = f"error: {str(e)}"

    try:
        # 检查 Tavily
        if not os.getenv("TAVILY_API_KEY"):
            tavily_status = "error: API_KEY not configured"
    except Exception as e:
        tavily_status = f"error: {str(e)}"

    return HealthResponse(
        status="ok" if db_status == "ok" and tavily_status == "ok" else "degraded",
        database=db_status,
        tavily=tavily_status,
        last_update=last_update,
    )


@app.get("/api/articles", response_model=list[ArticleResponse])
async def list_articles(
    category: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
):
    """获取文章列表"""
    try:
        with get_db() as db:
            articles = get_articles(db, category=category, limit=limit, offset=offset)
            return [ArticleResponse(**article.to_dict()) for article in articles]
    except Exception as e:
        logger.error(f"获取文章列表失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/articles/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: int):
    """获取单篇文章详情"""
    try:
        with get_db() as db:
            article = get_article_by_id(db, article_id)
            if not article:
                raise HTTPException(status_code=404, detail="文章不存在")
            return ArticleResponse(**article.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文章失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/articles/{article_id}/original")
async def get_original_content(article_id: int):
    """获取净化后的原文"""
    try:
        with get_db() as db:
            article = get_article_by_id(db, article_id)
            if not article:
                raise HTTPException(status_code=404, detail="文章不存在")

            # 如果已有内容，直接返回
            if article.content:
                return {
                    "title": article.title,
                    "content": article.content,
                    "image_urls": json.loads(article.image_urls) if article.image_urls else [],
                }

            # 否则实时抓取
            fetcher = ArticleFetcher()
            result = fetcher.fetch(article.url)
            if result:
                # 更新数据库
                content, summary = content_cleaner.clean(result["content"])
                update_article(
                    db,
                    article_id,
                    {
                        "content": content,
                        "summary": summary or article.summary,
                        "image_urls": json.dumps(result["image_urls"][:5]),
                        "is_processed": True,
                    },
                )
                return {
                    "title": result["title"],
                    "content": content,
                    "image_urls": result["image_urls"][:5],
                }

            raise HTTPException(status_code=500, detail="抓取原文失败")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取原文失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/fetch")
async def trigger_fetch(request: FetchRequest, background_tasks: BackgroundTasks):
    """手动触发抓取任务"""
    try:
        # 在后台执行抓取
        background_tasks.add_task(run_fetch_task, request.categories)
        return {
            "status": "accepted",
            "message": "抓取任务已启动，请稍后查看结果",
        }
    except Exception as e:
        logger.error(f"触发抓取失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 后台任务 ====================


def run_fetch_task(categories: Optional[list[str]] = None):
    """执行抓取任务"""
    logger.info(f"开始抓取任务，categories={categories}")

    try:
        # 初始化搜索器
        searcher = TavilySearcher()

        # 获取已存在的 URL（去重）
        with get_db() as db:
            existing_urls = {article.url for article in db.query(Article).all()}

        # 搜索
        if categories:
            category_results = {}
            for cat in categories:
                category_results[cat] = searcher.search_category(cat)
        else:
            category_results = searcher.search_all_categories()

        # 去重并保存
        total_new = 0
        for category, articles in category_results.items():
            # 去重
            unique_articles = deduplicate_articles(articles, existing_urls)

            # 保存到数据库
            with get_db() as db:
                for article_data in unique_articles:
                    # 检查是否已存在
                    if get_article_by_url(db, article_data["url"]):
                        continue

                    # 创建文章记录
                    article = create_article(
                        db,
                        {
                            "title": article_data["title"],
                            "category": category,
                            "url": article_data["url"],
                            "source": article_data["source"],
                            "summary": article_data["summary"],
                            "published_at": article_data["published_at"],
                            "is_processed": False,
                        },
                    )

                    # 抓取原文
                    logger.info(f"抓取原文：{article.url}")
                    try:
                        fetch_result = article_fetcher.fetch(article.url)
                        if fetch_result and fetch_result.get("content"):
                            # 清洗内容
                            content, summary = content_cleaner.clean(fetch_result["content"])

                            # 下载图片
                            local_images = image_processor.download_images(
                                fetch_result["image_urls"], article.id
                            )

                            # 更新文章
                            update_article(
                                db,
                                article.id,
                                {
                                    "content": content,
                                    "summary": summary or article.summary,
                                    "author": fetch_result.get("author"),
                                    "image_urls": json.dumps(local_images[:5]),
                                    "is_processed": True,
                                },
                            )
                        else:
                            # 抓取失败，标记为已处理（至少保存了元数据）
                            update_article(db, article.id, {"is_processed": True})
                    except Exception as e:
                        logger.error(f"抓取原文失败 {article.url}: {e}")
                        # 继续处理下一篇文章

                    total_new += 1

        logger.info(f"抓取任务完成，新增 {total_new} 篇文章")

    except Exception as e:
        logger.error(f"抓取任务失败：{e}", exc_info=True)


# ==================== 定时任务 ====================


def setup_scheduler():
    """设置定时任务"""
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger

    scheduler = BackgroundScheduler()

    # 每天早晨 7:00 执行抓取
    scheduler.add_job(
        run_fetch_task,
        CronTrigger(hour=7, minute=0),
        id="daily_fetch",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("定时任务已启动：每天 7:00 自动抓取")

    return scheduler


# 应用启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动"""
    # 初始化数据库
    init_db()
    logger.info("数据库初始化完成")

    # 启动定时任务
    if os.getenv("SCHEDULER_ENABLED", "true").lower() == "true":
        setup_scheduler()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
