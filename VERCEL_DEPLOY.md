# 🚀 Vercel 部署指南

## 快速部署（5 分钟）

### 方式 1: Vercel 网页部署（推荐，最简单）

**步骤**：

1. **打开 Vercel**
   访问：https://vercel.com/new

2. **导入 GitHub 仓库**
   - 点击 "Import Git Repository"
   - 选择 `JunChen19/apple-shrimp-news`
   - 点击 "Import"

3. **配置项目**
   - **Framework Preset**: Next.js (自动检测)
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next` (默认)

4. **添加环境变量**
   ```
   NEXT_PUBLIC_API_URL = https://your-backend-url.com
   ```
   （暂时可以留空，等后端部署后再添加）

5. **点击 "Deploy"**
   - 等待 2-3 分钟
   - 部署成功后会显示访问链接

6. **完成！**
   - 访问分配的域名（如 `apple-shrimp-news.vercel.app`）
   - 可以绑定自定义域名（可选）

---

### 方式 2: Vercel CLI 部署

**前提**：已安装 Vercel CLI 并登录

```bash
# 1. 安装 Vercel CLI（如果未安装）
npm install -g vercel

# 2. 登录 Vercel
vercel login

# 3. 进入前端目录
cd frontend

# 4. 部署到生产环境
vercel --prod
```

**首次部署**会提示：
- Set up and deploy? **Y**
- Which scope? 选择你的账号
- Link to existing project? **N**
- Project name? **apple-shrimp-news**
- Directory? **./frontend** (或直接在前端目录执行)
- Want to modify settings? **N**

**部署完成后**：
- 会显示预览链接和正式链接
- 访问链接即可查看完整前端

---

## 部署后配置

### 1. 配置后端 API 地址

在 Vercel Dashboard：
1. 进入项目 → Settings → Environment Variables
2. 添加变量：
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: 后端 API 地址（如 `https://your-backend.com`）
3. 重新部署（会自动触发）

### 2. 绑定自定义域名（可选）

1. Settings → Domains
2. 添加域名（如 `news.example.com`）
3. 按提示配置 DNS（CNAME 记录）

---

## 自动部署

部署后，每次推送到 main 分支都会自动部署：

```bash
git push origin main
# Vercel 会自动构建并部署
```

---

## 故障排查

### 构建失败

**错误**: `Module not found`
- 解决：确保在 `frontend` 目录执行
- 检查 `package.json` 依赖是否完整

**错误**: `generateStaticParams()`
- 解决：Vercel 支持 SSR，不需要静态导出
- 确保 `next.config.js` 没有 `output: 'export'`

### 页面空白

- 检查浏览器控制台错误
- 确认环境变量已配置
- 查看 Vercel Functions 日志

---

## 费用说明

**Hobby 计划（免费）**：
- ✅ 无限部署
- ✅ 自动 SSL
- ✅ 全球 CDN
- ✅ 100GB 带宽/月
- ✅ 支持 SSR 和 Serverless Functions

**适合个人项目和演示**

---

## 部署后的链接

部署成功后，Vercel 会提供：
- 生产链接：`https://apple-shrimp-news.vercel.app`
- 预览链接：每次 PR 都会生成

**将链接添加到 GitHub 仓库描述中！**

---

## 下一步：部署后端

前端部署完成后，可以部署后端 API：

**推荐平台**：
- **Render**: https://render.com (免费，支持 Python)
- **Railway**: https://railway.app (免费额度)
- **Fly.io**: https://fly.io (免费额度)

部署后端后，在 Vercel 添加环境变量 `NEXT_PUBLIC_API_URL` 即可连接。

---

**需要帮助？** 随时问我！
