"""
数据库连接管理 - 异步 SQLAlchemy 引擎与会话工厂
支持 CockroachDB / PostgreSQL（生产）和 SQLite（本地开发/测试）
"""
import ssl as _ssl
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


def _build_url(raw: str) -> str:
    """将 DATABASE_URL 转为 asyncpg 兼容格式。

    处理逻辑：
    - sqlite → 原样返回
    - cockroachdb+asyncpg → 原样（去掉 sslmode 改用 ssl 对象）
    - postgresql:// 或 postgresql+asyncpg:// → 自动检测并使用合适 dialect
    """
    if raw.startswith("sqlite"):
        return raw

    parsed = urlparse(raw)
    params = parse_qs(parsed.query)
    params.pop("sslmode", None)
    params.pop("channel_binding", None)

    if raw.startswith("cockroachdb"):
        new_scheme = parsed.scheme
    elif "cockroach" in parsed.hostname or "cockroach" in raw:
        new_scheme = "cockroachdb+asyncpg"
    else:
        new_scheme = "postgresql+asyncpg"

    clean_query = urlencode({k: v[0] for k, v in params.items()})
    return urlunparse((new_scheme, parsed.netloc, parsed.path,
                       parsed.params, clean_query, parsed.fragment))


_is_sqlite = settings.DATABASE_URL.startswith("sqlite")
_db_url = _build_url(settings.DATABASE_URL)

_engine_kwargs = {
    "echo": settings.DATABASE_ECHO,
}

if _is_sqlite:
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    _engine_kwargs["pool_pre_ping"] = True
    _engine_kwargs["pool_size"] = 10
    _engine_kwargs["max_overflow"] = 20
    _ssl_ctx = _ssl.create_default_context()
    _engine_kwargs["connect_args"] = {"ssl": _ssl_ctx}

engine = create_async_engine(_db_url, **_engine_kwargs)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """FastAPI 依赖注入：获取数据库会话"""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
