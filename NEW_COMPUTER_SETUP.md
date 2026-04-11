# 🖥️ 换电脑开发 / 迁移指南 (RexMatch)

由于我们的数据库 (CockroachDB)、缓存 (Upstash Redis) 和存储 (Supabase S3) **都已经部署在云端**，所以你在新电脑上**完全不需要迁移任何本地数据**（没有本地数据库文件需要拷贝）。

你要做的仅仅是：**迁移代码 ➡️ 恢复环境变量 ➡️ 安装依赖 ➡️ 运行**。

下面是详细的步骤：

## ☁️ 常用云服务控制台快捷入口
如果你在新电脑上需要查看数据、重启服务或找回配置，可以直接访问以下我们在用的云服务控制台：
- **代码仓库 (GitHub)**: https://github.com/rexrex1233/rexmatch
- **服务器部署 (Render)**: https://dashboard.render.com (用于查看前后端日志和重新部署)
- **数据库 (CockroachDB)**: https://cockroachlabs.cloud (用于查看用户数据、执行 SQL 语句)
- **缓存 (Upstash)**: https://console.upstash.com (用于查看 Redis 数据、清空缓存)
- **对象存储 (Supabase)**: https://supabase.com/dashboard (用于查看和管理用户上传的照片)

---

## 1. 代码迁移
由于你已经把代码推送到 GitHub (或其他远端仓库)，你可以在新电脑上直接 Clone，或者把你现在的 `rex_match` 文件夹打个压缩包发到新电脑上解压。

```bash
# 如果通过 Git 迁移：
git clone https://github.com/rexrex1233/rexmatch.git
cd rexmatch
```

---

## 2. 🔑 核心操作：迁移环境变量 (极其重要)

**注意：** 因为包含敏感密码的 `.env` 文件默认被 `.gitignore` 忽略了，所以不会同步到 Git 仓库上。如果你是通过 Git 迁的代码，新电脑上会缺失配置文件！

你需要在**旧电脑**上，找到以下文件并复制到新电脑对应的目录：

- **后端环境变量：** 复制 `backend/.env`
- **前端环境变量：** 复制 `miniprogram/.env.development` 和 `miniprogram/.env.production` (如果存在的话，主要是 API Base URL)

> **💡 备用方案：** 
> 如果你忘记拷贝旧电脑的 `.env`，你可以在新电脑上复制 `backend/.env.example` 为 `backend/.env`，然后去对应的云平台 (CockroachDB, Upstash, Supabase) 重新复制一下连接串填进去，即可恢复。

---

## 3. 后端环境恢复 (Python)

在新电脑上，你需要重新安装 Python 环境（建议 Python 3.10+）。

```bash
cd backend

# 1. 创建全新的虚拟环境 (不要把旧电脑的 venv 文件夹直接考过来，会报错)
python -m venv venv

# 2. 激活虚拟环境
# macOS / Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt
```

> **测试后端是否正常：**
> 输入命令 `uvicorn app.main:app --reload --port 9000`，如果没报错且显示 Application startup complete，说明云端数据库连接成功！

---

## 4. 前端环境恢复 (Vue / uni-app)

在新电脑上，你需要确保安装了 **Node.js** 和 **HBuilderX**。

```bash
cd miniprogram

# 安装 Node 依赖 (如果存在 package.json 的话，uni-app CLI 项目需要)
npm install 
# 或者 yarn install / pnpm install
```

**运行方式：**
由于我们是 HBuilderX 创建的 uni-app 项目：
1. 打开新电脑上的 **HBuilderX**。
2. 将 `rex_match/miniprogram` 文件夹拖入 HBuilderX 工作区。
3. 点击顶部菜单：**运行** -> **运行到内置浏览器 / 运行到小程序模拟器**。

---

## 🎉 常见问题排查

1. **后端启动报错 "Database connection failed" / "password authentication failed"**
   - 检查 `backend/.env` 中的 `DATABASE_URL` 是否复制正确。
   - 由于使用的是云数据库 CockroachDB，只要网络通畅且密码正确，任何电脑都能连上你原来的数据。

2. **前端页面一直在 Loading 或 接口请求 404**
   - 检查新电脑是不是没启动本地 Python 后端 (端口默认 9000)。
   - 检查 `miniprogram/.env.development` 中的 `VITE_API_BASE_URL` 是否正确指向 `http://127.0.0.1:9000/api/v1`（如果是运行在模拟器或手机上，可能需要将 `127.0.0.1` 换成你新电脑的局域网 IP，如 `192.168.x.x`）。

3. **照片无法上传 / 加载失败**
   - 检查 `backend/.env` 中的 `S3_xxx` 等 Supabase Storage 配置是否完整。

---
*有了这份指南，你换多少台电脑都可以随时随地继续开发我们的 App！*
