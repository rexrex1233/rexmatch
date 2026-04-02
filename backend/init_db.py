"""
生产环境数据库初始化 - 创建表 + 种子数据
用法: python init_db.py
"""
import asyncio
from app.core.database import engine, Base
from app.models import *  # noqa: F401,F403 - 确保所有模型被导入


async def init():
    print("🔧 创建数据库表...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ 数据库表创建完成")

    from app.utils.seed_data import seed
    await seed()
    print("✅ 初始化完成")


if __name__ == "__main__":
    asyncio.run(init())
