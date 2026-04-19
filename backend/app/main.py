"""
RexMatch - 交友匹配平台 FastAPI 应用入口
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_v1_router


async def _ensure_columns():
    """
    幂等地补齐数据库新列（ADD COLUMN IF NOT EXISTS）。
    适用于生产库通过 create_all 建立、没有 alembic_version 的情况。
    """
    from sqlalchemy import text
    from app.core.database import engine

    statements = [
        # migration 006 — swipes.re_eligible
        "ALTER TABLE swipes ADD COLUMN IF NOT EXISTS re_eligible BOOLEAN NOT NULL DEFAULT FALSE",
        # migration 007 — users 扩展资料字段
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS mbti VARCHAR(4)",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS hometown VARCHAR(50)",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS school VARCHAR(50)",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS study_status VARCHAR(20)",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS industry VARCHAR(50)",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS marital_status VARCHAR(20)",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS dating_purpose VARCHAR(50)",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS dating_rhythm VARCHAR(50)",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS meeting_scenarios VARCHAR(255)",
    ]

    async with engine.begin() as conn:
        for sql in statements:
            try:
                await conn.execute(text(sql))
            except Exception as e:
                print(f"⚠️  列补齐跳过（可能已存在）: {e}")

    print("✅ 数据库列补齐完成")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    from app.core.redis import get_redis, close_redis
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} 启动中...")
    print(f"   DEBUG={settings.DEBUG}, DB={'SQLite' if 'sqlite' in settings.DATABASE_URL else 'PostgreSQL'}")
    print(f"   S3={'ON' if settings.use_s3 else 'OFF (local uploads)'}")
    await _ensure_columns()
    await get_redis()
    yield
    await close_redis()
    print(f"👋 {settings.APP_NAME} 正在关闭...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="交友匹配平台 API",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

if not settings.use_s3:
    from starlette.staticfiles import StaticFiles
    _uploads_dir = Path(__file__).resolve().parent.parent / "uploads"
    _uploads_dir.mkdir(exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(_uploads_dir)), name="uploads")


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}
