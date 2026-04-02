# RexMatch 免费部署指南

> 全部使用免费服务，月费 $0

## 架构总览

```
用户 → Render (后端 FastAPI)  → CockroachDB (分布式 SQL, 10GB 免费)
                              → Upstash (Redis)
                              → Cloudflare R2 (图片)
```

---

## 第 1 步：注册免费服务（10 分钟）

### 1.1 CockroachDB Cloud — 免费 10GB 分布式数据库

1. 访问 https://cockroachlabs.cloud → Sign Up（支持 GitHub / Google 登录）
2. Create Cluster：
   - **Plan**: Basic (Free)
   - **Cloud Provider**: AWS
   - **Region**: `us-east-1`（或离用户最近的）
3. 创建完成后，进入 Connect 页面：
   - 选择语言 **Python**，驱动 **SQLAlchemy (asyncpg)**
   - 复制连接串，格式如：
   ```
   cockroachdb+asyncpg://username:password@xxx-xxx.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full
   ```
4. 系统会自动处理 SSL 和 sslmode 参数，直接使用即可

### 1.2 Upstash — 免费 Redis

1. 访问 https://upstash.com → Sign Up
2. 创建 Redis 数据库：名称 `rexmatch`，Region 选 `US East 1`
3. 在数据库详情页，复制 **Endpoint**（`rediss://` 开头的完整 URL）：
   ```
   rediss://default:xxx@us1-xxx.upstash.io:6379
   ```

### 1.3 Cloudflare R2 — 免费对象存储

1. 访问 https://dash.cloudflare.com → 注册（需绑卡但不会扣费）
2. 左侧菜单 → R2 → Create bucket，名称 `rexmatch`
3. Settings → Public Access → 开启，记下公开 URL：
   ```
   https://pub-xxx.r2.dev
   ```
4. Manage R2 API Tokens → Create API Token：
   - 权限：Object Read & Write
   - 指定 bucket：`rexmatch`
   - 记下 `Access Key ID` 和 `Secret Access Key`
5. 记下你的 Account ID（在 R2 概览页右侧），拼出 endpoint：
   ```
   https://YOUR_ACCOUNT_ID.r2.cloudflarestorage.com
   ```

### 1.4 Render — 免费后端托管

1. 访问 https://render.com → Sign Up（支持 GitHub 登录）
2. 暂时不创建服务，等代码推到 GitHub 后再配置

---

## 第 2 步：推送代码到 GitHub（3 分钟）

```bash
cd rex_match
git init
git add .
git commit -m "initial commit"

# 在 GitHub 创建仓库 rexmatch，然后：
git remote add origin https://github.com/YOUR_USERNAME/rexmatch.git
git push -u origin main
```

---

## 第 3 步：部署后端到 Render（5 分钟）

1. Render Dashboard → New → Web Service
2. 连接你的 GitHub 仓库
3. 配置：
   - **Name**: `rexmatch-api`
   - **Root Directory**: `backend`
   - **Runtime**: Docker
   - **Instance Type**: Free
4. 添加环境变量（Environment → Add Environment Variable）：

| Key | Value |
|-----|-------|
| `DEBUG` | `false` |
| `SECRET_KEY` | （点 Generate 生成随机值） |
| `DATABASE_URL` | `cockroachdb+asyncpg://...`（第 1.1 步的值） |
| `REDIS_URL` | `rediss://default:...`（第 1.2 步的值） |
| `S3_ENDPOINT_URL` | `https://xxx.r2.cloudflarestorage.com`（第 1.3 步） |
| `S3_ACCESS_KEY_ID` | （第 1.3 步的值） |
| `S3_SECRET_ACCESS_KEY` | （第 1.3 步的值） |
| `S3_BUCKET_NAME` | `rexmatch` |
| `S3_PUBLIC_URL` | `https://pub-xxx.r2.dev` |
| `ALLOWED_ORIGINS` | `https://rexmatch-api.onrender.com` |

5. 点 Create Web Service → 等待构建部署（约 3-5 分钟）
6. 部署完成后访问 `https://rexmatch-api.onrender.com/health` 验证

---

## 第 4 步：初始化数据库（2 分钟）

Render 部署成功后，需要初始化数据库表和种子数据。

**方法 A：通过 Render Shell**
1. Render Dashboard → 你的服务 → Shell
2. 运行：
   ```bash
   python init_db.py
   ```

**方法 B：本地执行（连接远程数据库）**
```bash
cd backend
export DATABASE_URL="cockroachdb+asyncpg://..."  # CockroachDB 连接串
source ../.venv/bin/activate
python init_db.py
```

---

## 第 5 步：部署前端（3 分钟）

### 方案 A：H5 静态站（最简单）

1. 修改 `miniprogram/.env.production`：
   ```
   VITE_API_BASE_URL=https://rexmatch-api.onrender.com/api/v1
   ```

2. 构建：
   ```bash
   cd miniprogram
   npm run build:h5
   ```

3. 在 Render 创建 Static Site：
   - Root Directory: `miniprogram/dist/build/h5`
   - 或者直接用 Cloudflare Pages 托管（更快、免费）

### 方案 B：微信小程序

1. 在微信公众平台注册小程序，获取 AppID
2. 配置服务器域名（需已备案域名 + HTTPS）
3. 在后端 `.env` 中设置 `WX_APP_ID` 和 `WX_APP_SECRET`
4. 构建并上传：
   ```bash
   cd miniprogram
   npm run build:mp-weixin
   ```
5. 用微信开发者工具打开 `dist/build/mp-weixin`，上传并提审

---

## 费用总结

| 服务 | 免费额度 | 超出后 |
|------|----------|--------|
| Render | 750 小时/月 | $7/月 |
| CockroachDB | **10GB 存储** + 50M RU/月 | 按用量计费 |
| Upstash Redis | 500K 命令/月 | $0.2/100K |
| Cloudflare R2 | 10GB + 免费流量 | $0.015/GB |
| **总计** | **$0/月** | 按需付费 |

---

## 本地开发

部署上线后，本地开发仍可继续用 SQLite：

```bash
cd backend
cp .env.example .env
# 编辑 .env，保持 DATABASE_URL 为 SQLite 即可
source ../.venv/bin/activate
uvicorn app.main:app --reload --port 9000
```

---

## 常见问题

**Q: Render 免费版会休眠？**
A: 是的，15 分钟无流量后休眠，下次访问约 30 秒冷启动。可以用 https://cron-job.org 每 14 分钟 ping 一次 `/health` 保活。

**Q: 数据库需要备份吗？**
A: CockroachDB Cloud 自动多副本复制，Basic 层自带自动备份。

**Q: 图片 CDN？**
A: Cloudflare R2 的公开访问自带全球 CDN，无需额外配置。

**Q: CockroachDB 和 PostgreSQL 有什么区别？**
A: CockroachDB 兼容 PostgreSQL 协议，你的代码无需改动。主要优势是分布式架构和 10GB 免费额度（Neon 仅 0.5GB）。
