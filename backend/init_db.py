"""
生产环境数据库初始化 - 运行 Alembic 迁移 + 种子数据
用法: python init_db.py
"""
import asyncio
from alembic.config import Config
from alembic import command


def run_migrations():
    """通过 Alembic 执行所有待跑的迁移（相当于 alembic upgrade head）"""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    print("✅ 数据库迁移完成")


async def seed():
    from app.utils.seed_data import seed as _seed
    await _seed()
    print("✅ 种子数据完成")


async def init():
    print("🔧 运行数据库迁移...")
    run_migrations()
    await seed()
    print("✅ 初始化完成")


if __name__ == "__main__":
    asyncio.run(init())
