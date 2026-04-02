# RexMatch - 交友匹配平台

类似「牵手」的交友匹配小程序，基于微信小程序 + Python FastAPI 全栈开发。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | uni-app (Vue 3) → 微信小程序 |
| 后端 | Python + FastAPI |
| 数据库 | PostgreSQL |
| 缓存 | Redis |
| ORM | SQLAlchemy 2.0 (async) |
| 迁移 | Alembic |
| 容器 | Docker + docker-compose |

## 项目结构

```
rex_match/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/          # API 路由（auth/users/discover/match/chat/report）
│   │   ├── core/            # 配置、安全、依赖注入
│   │   ├── models/          # SQLAlchemy ORM 模型
│   │   ├── schemas/         # Pydantic 请求/响应模型
│   │   ├── services/        # 业务逻辑层
│   │   └── utils/           # 工具函数、种子数据
│   ├── alembic/             # 数据库迁移
│   ├── Dockerfile
│   └── requirements.txt
├── miniprogram/             # 微信小程序（uni-app）
│   ├── src/
│   │   ├── pages/           # 页面（login/home/discover/chat/profile 等）
│   │   ├── components/      # 公共组件
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── api/             # API 请求封装
│   │   └── utils/           # 工具函数
│   └── package.json
└── docker-compose.yml       # 本地开发一键启动
```

## 快速开始

### 方式一：Docker 一键启动（推荐）

```bash
# 启动 PostgreSQL + Redis + FastAPI 后端
docker-compose up -d

# 初始化种子数据（兴趣标签 + 测试用户）
docker-compose exec backend python -m app.utils.seed_data

# API 文档地址
open http://localhost:8000/docs
```

### 方式二：本地开发

**后端：**

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量
cp .env.example .env

# 确保本地 PostgreSQL 和 Redis 已启动，然后：
# 初始化数据库表
python -m app.utils.seed_data

# 启动开发服务器
uvicorn app.main:app --reload --port 8000
```

**前端（小程序）：**

```bash
cd miniprogram

# 安装依赖
npm install

# 编译到微信小程序
npm run dev:mp-weixin

# 用微信开发者工具打开 dist/dev/mp-weixin 目录
```

## API 概览

| 模块 | 路径 | 说明 |
|------|------|------|
| 认证 | `POST /api/v1/auth/wx-login` | 微信登录 |
| 用户 | `GET/PUT /api/v1/users/me` | 获取/更新个人资料 |
| 发现 | `GET /api/v1/discover/recommend` | 推荐用户列表 |
| 匹配 | `POST /api/v1/match/swipe` | 喜欢/跳过 |
| 匹配 | `GET /api/v1/match/list` | 我的匹配 |
| 聊天 | `GET /api/v1/chat/list` | 聊天列表 |
| 聊天 | `POST /api/v1/chat/send` | 发送消息 |
| 举报 | `POST /api/v1/report/submit` | 举报用户 |
| 举报 | `POST /api/v1/report/block` | 拉黑用户 |

启动后访问 `http://localhost:8000/docs` 查看完整 Swagger 文档。

## 核心功能

- **微信登录**：小程序授权一键登录，JWT token 认证
- **用户资料**：头像、昵称、性别、年龄、城市、简介、兴趣标签
- **推荐浏览**：卡片式浏览，支持按性别/年龄/城市筛选
- **喜欢/跳过**：双向喜欢即匹配，每日点赞次数限制
- **即时聊天**：匹配后文字聊天（轮询，后续升级 WebSocket）
- **举报拉黑**：用户安全机制

## 后续规划

- [ ] WebSocket 实时聊天
- [ ] 图片消息
- [ ] AI 推荐算法
- [ ] 微信模板消息推送
- [ ] 腾讯云 COS 图片上传
- [ ] VIP 会员体系
