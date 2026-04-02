"""
应用配置管理 - 通过环境变量加载所有配置项
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 应用基础配置
    APP_NAME: str = "RexMatch"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # 允许的前端域名（逗号分隔），DEBUG=True 时允许所有
    ALLOWED_ORIGINS: str = ""

    # 数据库
    DATABASE_URL: str = "sqlite+aiosqlite:///./rex_match.db"
    DATABASE_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT 认证
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天

    # 微信小程序
    WX_APP_ID: str = ""
    WX_APP_SECRET: str = ""

    # S3 兼容对象存储（Cloudflare R2 / AWS S3 / 腾讯 COS）
    S3_ENDPOINT_URL: Optional[str] = None
    S3_ACCESS_KEY_ID: Optional[str] = None
    S3_SECRET_ACCESS_KEY: Optional[str] = None
    S3_BUCKET_NAME: Optional[str] = None
    S3_PUBLIC_URL: Optional[str] = None  # 公开访问 URL 前缀
    S3_REGION: Optional[str] = None

    # 每日推荐配置
    DAILY_RECOMMEND_LIMIT: int = 20
    DAILY_LIKE_LIMIT: int = 10

    @property
    def use_s3(self) -> bool:
        return bool(self.S3_ENDPOINT_URL and self.S3_ACCESS_KEY_ID and self.S3_BUCKET_NAME)

    @property
    def cors_origins(self) -> list[str]:
        if self.DEBUG:
            return ["*"]
        if self.ALLOWED_ORIGINS:
            return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]
        return []

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()
