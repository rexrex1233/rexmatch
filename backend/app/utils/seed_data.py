"""
种子数据 - 预定义兴趣标签 + 测试用户数据
运行: python -m app.utils.seed_data
"""
import asyncio
from datetime import date

from sqlalchemy import select

from app.core.database import engine, async_session_factory, Base
from app.models.interest import Interest
from app.models.user import User
from app.models.profile import Profile
from app.models.photo import Photo
from app.models.interest import UserInterest

INTEREST_DATA = [
    ("运动", ["健身", "跑步", "瑜伽", "游泳", "篮球", "羽毛球", "骑行", "登山"]),
    ("音乐", ["唱歌", "吉他", "钢琴", "说唱", "电音", "古典乐", "摇滚"]),
    ("美食", ["烘焙", "下厨", "火锅", "咖啡", "甜品", "日料", "烧烤"]),
    ("旅行", ["自驾游", "背包客", "海岛游", "城市探索", "露营", "滑雪"]),
    ("影视", ["电影", "追剧", "动漫", "综艺", "纪录片"]),
    ("阅读", ["小说", "历史", "科幻", "心理学", "哲学", "漫画"]),
    ("游戏", ["手游", "PC游戏", "主机游戏", "桌游", "剧本杀"]),
    ("艺术", ["摄影", "绘画", "书法", "设计", "手工"]),
    ("社交", ["狼人杀", "密室逃脱", "派对", "clubhouse"]),
    ("宠物", ["猫", "狗", "兔子", "仓鼠", "鱼"]),
]

DEMO_USERS = [
    {
        "openid": "demo_user_001",
        "nickname": "小明",
        "gender": 1,
        "birthday": date(1998, 5, 15),
        "city": "深圳",
        "province": "广东",
        "bio": "喜欢运动和音乐的程序员，周末一般在爬山或弹吉他",
        "height": 178,
        "education": "本科",
        "occupation": "软件工程师",
    },
    {
        "openid": "demo_user_002",
        "nickname": "小红",
        "gender": 2,
        "birthday": date(1999, 8, 22),
        "city": "深圳",
        "province": "广东",
        "bio": "热爱旅行和摄影，希望找到一起看世界的人 🌍",
        "height": 165,
        "education": "硕士",
        "occupation": "产品经理",
    },
    {
        "openid": "demo_user_003",
        "nickname": "阿杰",
        "gender": 1,
        "birthday": date(1997, 3, 10),
        "city": "广州",
        "province": "广东",
        "bio": "厨艺达人，可以为你做一桌好菜",
        "height": 175,
        "education": "本科",
        "occupation": "市场运营",
    },
    {
        "openid": "demo_user_004",
        "nickname": "Luna",
        "gender": 2,
        "birthday": date(2000, 1, 5),
        "city": "北京",
        "province": "北京",
        "bio": "书虫 + 咖啡爱好者，最近在学习心理学",
        "height": 163,
        "education": "本科",
        "occupation": "UI设计师",
    },
    {
        "openid": "demo_user_005",
        "nickname": "大卫",
        "gender": 1,
        "birthday": date(1996, 11, 28),
        "city": "上海",
        "province": "上海",
        "bio": "金融狗一枚，工作之余喜欢打篮球和看电影",
        "height": 182,
        "education": "硕士",
        "occupation": "金融分析师",
    },
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as db:
        existing = await db.execute(select(Interest).limit(1))
        if existing.scalar_one_or_none() is not None:
            print("种子数据已存在，跳过")
            return

        interest_map = {}
        for category, names in INTEREST_DATA:
            for name in names:
                interest = Interest(name=name, category=category)
                db.add(interest)
                await db.flush()
                interest_map[name] = interest.id

        print(f"✅ 已创建 {len(interest_map)} 个兴趣标签")

        for user_data in DEMO_USERS:
            openid = user_data.pop("openid")
            nickname = user_data.pop("nickname")
            gender = user_data.pop("gender")

            user = User(openid=openid)
            db.add(user)
            await db.flush()

            profile = Profile(
                user_id=user.id,
                nickname=nickname,
                gender=gender,
                is_complete=True,
                **user_data,
            )
            db.add(profile)
            await db.flush()

            photo = Photo(
                user_id=user.id,
                url=f"https://api.dicebear.com/7.x/avataaars/svg?seed={nickname}",
                is_avatar=True,
                sort_order=0,
            )
            db.add(photo)

        await db.commit()
        print(f"✅ 已创建 {len(DEMO_USERS)} 个测试用户")


if __name__ == "__main__":
    asyncio.run(seed())
