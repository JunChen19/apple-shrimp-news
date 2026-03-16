# 🦐 苹果虾资讯

AI 资讯聚合平台 - 每日自动更新

## 功能特性

- ✅ **四大板块**：大模型动态、AI 行业资讯、国际政治、金融板块
- ✅ **Tavily 搜索**：智能定向搜索，多源聚合
- ✅ **原文抓取**：自动抓取并净化原文，过滤广告
- ✅ **定时更新**：每天早晨 7:00 自动更新
- ✅ **响应式设计**：PC 和移动端完美适配
- ✅ **GitHub Pages 部署**：一键推送静态站点

## 快速启动

### 1. 配置环境变量

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑 .env 文件，Tavily API Key 已配置
```

### 2. Docker 一键启动（推荐）

```bash
docker-compose up -d
```

访问：
- 前端：http://localhost:3000
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

### 3. 本地开发环境

#### 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 启动服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:3000

### 4. 手动触发抓取

```bash
# 方式 1：使用脚本
cd backend
source venv/bin/activate
python ../scripts/fetch_all.py

# 方式 2：调用 API
curl -X POST http://localhost:8000/api/fetch \
  -H "Content-Type: application/json" \
  -d '{"categories": ["llm", "industry", "politics", "finance"]}'
```

### 5. 导出静态页面

```bash
cd frontend
npm run build
npm run export

# 输出目录：out/
```

## 目录结构

```
apple-shrimp-news/
├── backend/              # Python 后端
│   ├── app/
│   │   ├── crawler/     # 爬虫模块
│   │   │   ├── tavily_search.py   # Tavily 搜索
│   │   │   ├── fetch.py           # 原文抓取
│   │   │   ├── clean.py           # 广告过滤
│   │   │   └── images.py          # 图片处理
│   │   ├── db/          # 数据库模块
│   │   └── main.py      # FastAPI 入口
│   ├── data/            # SQLite 数据库
│   ├── logs/            # 日志文件
│   └── requirements.txt
├── frontend/            # Next.js 前端
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx              # 首页
│   │   │   ├── news/[category]/      # 板块列表页
│   │   │   └── article/[id]/         # 文章详情页
│   │   └── globals.css
│   └── next.config.js
├── scripts/             # 工具脚本
│   ├── fetch_all.py     # 全量抓取
│   ├── export_static.py # 导出静态页
│   └── start_frontend.sh
├── .github/workflows/   # GitHub Actions
├── docker-compose.yml
└── README.md
```

## API 接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/articles` | GET | 获取文章列表 |
| `/api/articles/:id` | GET | 获取文章详情 |
| `/api/articles/:id/original` | GET | 获取净化原文 |
| `/api/fetch` | POST | 手动触发抓取 |
| `/api/health` | GET | 健康检查 |

### 测试示例

```bash
# 健康检查
curl http://localhost:8000/api/health

# 获取文章列表
curl http://localhost:8000/api/articles?limit=10

# 按分类获取
curl http://localhost:8000/api/articles?category=llm

# 获取文章详情
curl http://localhost:8000/api/articles/5

# 手动触发抓取
curl -X POST http://localhost:8000/api/fetch \
  -H "Content-Type: application/json" \
  -d '{"categories": ["llm"]}'
```

## 部署到 GitHub Pages

### 方式一：GitHub Actions（自动）

1. 在 GitHub Settings → Secrets 添加：
   - `TAVILY_API_KEY`

2. 推送代码到 main 分支：
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

3. Actions 会自动构建并部署到 gh-pages 分支

### 方式二：手动部署

```bash
# 1. 构建前端
cd frontend
npm run build

# 2. 安装 gh-pages
npm install -g gh-pages

# 3. 部署
gh-pages -d out
```

访问：https://your-username.github.io/apple-shrimp-news

## 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `TAVILY_API_KEY` | Tavily API Key（必填） | - |
| `DATABASE_URL` | 数据库连接 | sqlite:///./backend/data/articles.db |
| `SCHEDULER_ENABLED` | 启用定时任务 | true |
| `SCHEDULER_HOUR` | 定时任务小时 | 7 |
| `SCHEDULER_MINUTE` | 定时任务分钟 | 0 |
| `NEXT_PUBLIC_API_URL` | 后端 API 地址 | http://localhost:8000 |

### 自定义域名

在根目录创建 `CNAME` 文件：

```
news.example.com
```

然后在域名服务商处配置 CNAME 记录。

## 日志查看

```bash
# 查看后端日志
tail -f backend/logs/app.log

# 查看定时任务日志
docker-compose logs backend
```

## 故障排查

### Tavily API 调用失败

检查 API Key 是否正确：
```bash
curl -H "Authorization: Bearer $TAVILY_API_KEY" https://api.tavily.com/search
```

### 数据库锁定

SQLite 同时写入可能锁定，重启服务：
```bash
docker-compose restart backend
```

### 前端无法连接后端

检查 API 地址配置：
```bash
# frontend/.env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 开发计划

- [x] 后端基础架构
- [x] Tavily 搜索集成
- [x] 原文抓取与清洗
- [x] 定时任务
- [x] 前端首页
- [x] 前端列表页
- [x] 前端详情页
- [ ] 搜索功能
- [ ] 用户收藏/订阅
- [ ] RSS 订阅输出
- [ ] 更多数据源接入

## 技术栈

- **后端**: Python 3.10 + FastAPI + SQLAlchemy + SQLite
- **爬虫**: Tavily API + BeautifulSoup4 + requests
- **定时任务**: APScheduler
- **前端**: Next.js 14 + TypeScript + Tailwind CSS
- **部署**: Docker + GitHub Actions

## 许可证

MIT License

## 反馈

Issues: https://github.com/your-username/apple-shrimp-news/issues
