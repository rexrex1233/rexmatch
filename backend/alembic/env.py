"""
Alembic 迁移环境配置 - 支持异步数据库引擎
"""
import asyncio
import os
from logging.config import fileConfig

from sqlalchemy.pool import NullPool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 导入所有模型，确保 metadata 完整
from app.models import *  # noqa: F401, F403
from app.core.database import Base, _build_url

target_metadata = Base.metadata


def _get_url() -> str:
    """优先读环境变量 DATABASE_URL，否则用 alembic.ini 里的值"""
    raw = os.environ.get("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    return _build_url(raw)


def run_migrations_offline() -> None:
    context.configure(
        url=_get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    import ssl as _ssl

    url = _get_url()
    engine_kwargs: dict = {"poolclass": NullPool}

    if not url.startswith("sqlite"):
        ssl_ctx = _ssl.create_default_context()
        engine_kwargs["connect_args"] = {"ssl": ssl_ctx}

    connectable = create_async_engine(url, **engine_kwargs)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
