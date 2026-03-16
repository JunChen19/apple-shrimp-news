# 📦 苹果虾资讯 - 部署指南

## 快速部署选项

### 选项 1: GitHub Pages（推荐，前端免费托管）

**适合场景**：快速上线，前端免费托管

**步骤**：

1. **创建 GitHub 仓库**
   ```bash
   cd /Users/junchen/.openclaw/workspace-leo/apple-shrimp-news
   git init
   git add .
   git commit -m "Initial commit: 苹果虾资讯"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/apple-shrimp-news.git
   git push -u origin main
   ```

2. **启用 GitHub Pages**
   - 进入仓库 Settings → Pages
   - Source 选择 "GitHub Actions"
   - 保存后会自动部署

3. **配置 Secrets**
   - Settings → Secrets and variables → Actions
   - 添加 `TAVILY_API_KEY`（如果需要后端也部署）

4. **访问前端**
   ```
   https://YOUR_USERNAME.github.io/apple-shrimp-news
   ```

**注意**：GitHub Pages 只有静态前端，需要配置后端 API 地址。

---

### 选项 2: Vercel（推荐，前后端一起）

**适合场景**：一键部署，自动 SSL

**步骤**：

1. **安装 Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **部署前端**
   ```bash
   cd frontend
   vercel login
   vercel --prod
   ```

3. **配置环境变量**
   - 在 Vercel Dashboard 添加 `NEXT_PUBLIC_API_URL`

**优点**：
- 自动 HTTPS
- 全球 CDN
- 自动部署（git push 触发）

---

### 选项 3: 本地部署（有公网 IP 时）

**适合场景**：自己有服务器或公网 IP

**步骤**：

1. **启动后端**
   ```bash
   cd backend
   source venv/bin/activate
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. **启动前端（生产模式）**
   ```bash
   cd frontend
   npm run build
   npm run start
   ```

3. **配置域名和反向代理（可选）**
   ```nginx
   # Nginx 配置示例
   server {
       listen 80;
       server_name news.example.com;
       
       location / {
           proxy_pass http://localhost:3000;
       }
       
       location /api {
           proxy_pass http://localhost:8000;
       }
   }
   ```

---

### 选项 4: 云服务部署后端

**推荐平台**：

| 平台 | 免费额度 | 特点 |
|------|---------|------|
| **Render** | 免费 | 支持 Python，自动部署 |
| **Railway** | $5 试用 | 简单易用 |
| **Fly.io** | 免费额度 | 全球部署 |
| **Hugging Face Spaces** | 免费 | 适合 AI 项目 |

**Render 部署示例**：

1. 创建 `render.yaml`：
   ```yaml
   services:
     - type: web
       name: apple-shrimp-backend
       env: python
       buildCommand: "pip install -r backend/requirements.txt"
       startCommand: "cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
       envVars:
         - key: TAVILY_API_KEY
           value: your-api-key
         - key: DATABASE_URL
           value: sqlite:///./data/articles.db
   ```

2. 推送到 GitHub 后，在 Render 连接仓库自动部署

---

## 部署后配置

### 1. 配置 API 地址

前端需要知道后端地址，修改 `frontend/.env`：

```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

### 2. 设置定时任务

后端定时任务（每天 7:00 抓取）需要持续运行的服务：

**方案 A**: 使用云服务（Render/Railway 自动运行）

**方案 B**: 使用 GitHub Actions 定时触发
```yaml
# .github/workflows/fetch-daily.yml
name: Daily Fetch

on:
  schedule:
    - cron: '0 23 * * *'  # UTC 23:00 = 北京时间 7:00
  workflow_dispatch:

jobs:
  fetch:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r backend/requirements.txt
      - name: Run fetch
        env:
          TAVILY_API_KEY: ${{ secrets.TAVILY_API_KEY }}
        run: |
          cd backend
          python ../scripts/fetch_all.py
```

**方案 C**: 本地服务器 cron 任务
```bash
# crontab -e
0 7 * * * cd /path/to/apple-shrimp-news && ./scripts/fetch_all.py
```

---

## 部署检查清单

部署前确认：

- [ ] Tavily API Key 已配置
- [ ] 数据库路径正确
- [ ] 前端 API 地址已更新
- [ ] 定时任务已启用
- [ ] 日志目录可写
- [ ] 端口未被占用

部署后验证：

- [ ] 前端可访问
- [ ] 后端 API 响应正常
- [ ] 健康检查通过 (`/api/health`)
- [ ] 定时任务运行中
- [ ] 文章数据正常显示

---

## 故障排查

### 前端无法连接后端

**检查**：
```bash
# 测试后端
curl https://your-backend-url.com/api/health

# 检查前端配置
cat frontend/.env
```

**解决**：更新 `NEXT_PUBLIC_API_URL` 并重新部署前端

### 定时任务不执行

**检查日志**：
```bash
tail -f logs/backend.log
```

**解决**：确认 SCHEDULER_ENABLED=true 且服务持续运行

### 数据库锁定

**解决**：
```bash
# 重启后端服务
pkill -f "uvicorn app.main:app"
# 重新启动
```

---

## 性能优化建议

### 1. 启用缓存

后端已配置 5 分钟缓存，可在 `next.config.js` 调整：

```javascript
next: { revalidate: 300 } // 5 分钟
```

### 2. 图片优化

- 使用 WebP 格式
- 压缩图片（tinypng.com）
- 使用 CDN

### 3. 数据库优化

数据量大时（>10000 篇）：
- 添加索引
- 定期清理旧数据
- 考虑 PostgreSQL

---

## 安全建议

1. **API Key 保护**
   - 不要提交到 git
   - 使用环境变量或 Secrets

2. **CORS 配置**
   - 生产环境限制域名
   - 修改 `backend/app/main.py` 的 `allow_origins`

3. **速率限制**
   - Tavily API 有配额限制
   - 考虑添加请求限流

---

## 联系支持

遇到问题？

- 查看日志：`logs/backend.log`
- 检查配置：`.env` 文件
- 重启服务：`pkill` + 重新启动脚本
