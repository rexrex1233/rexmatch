"""
RexMatch - 交友匹配平台 FastAPI 应用入口
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_v1_router


def _run_migrations():
    """启动时自动执行待跑的 Alembic 迁移"""
    try:
        from alembic.config import Config
        from alembic import command
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("✅ 数据库迁移完成")
    except Exception as e:
        print(f"⚠️  数据库迁移失败: {e}")
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    from app.core.redis import get_redis, close_redis
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} 启动中...")
    print(f"   DEBUG={settings.DEBUG}, DB={'SQLite' if 'sqlite' in settings.DATABASE_URL else 'PostgreSQL'}")
    print(f"   S3={'ON' if settings.use_s3 else 'OFF (local uploads)'}")
    _run_migrations()
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
