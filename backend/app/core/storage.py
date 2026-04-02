"""
文件存储抽象层 - 支持本地存储和 S3 兼容对象存储
（Supabase Storage / Cloudflare R2 / AWS S3）
通过 S3_ENDPOINT_URL 环境变量自动切换
"""
import uuid
import logging
from pathlib import Path
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

_s3_client = None


def _get_s3_client():
    global _s3_client
    if _s3_client is not None:
        return _s3_client
    try:
        import boto3
        from botocore.config import Config

        s3_config = Config(s3={"addressing_style": "path"})
        _s3_client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            region_name=settings.S3_REGION or "us-east-1",
            config=s3_config,
        )
        return _s3_client
    except ImportError:
        logger.warning("boto3 未安装，使用本地存储")
        return None
    except Exception as e:
        logger.warning(f"S3 客户端初始化失败: {e}")
        return None


async def upload_file(content: bytes, user_id: int, ext: str, is_avatar: bool = False) -> str:
    """
    上传文件，返回可访问的 URL。
    如果配置了 S3 则上传到云端，否则存本地。
    """
    filename = f"{user_id}_{uuid.uuid4().hex[:12]}{ext}"
    object_key = f"photos/{user_id}/{filename}"

    if settings.use_s3:
        return await _upload_to_s3(content, object_key, ext)
    else:
        return _upload_to_local(content, user_id, filename)


async def _upload_to_s3(content: bytes, object_key: str, ext: str) -> str:
    client = _get_s3_client()
    if client is None:
        raise RuntimeError("S3 客户端不可用")

    content_type_map = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp",
    }
    content_type = content_type_map.get(ext, "application/octet-stream")

    client.put_object(
        Bucket=settings.S3_BUCKET_NAME,
        Key=object_key,
        Body=content,
        ContentType=content_type,
    )

    if settings.S3_PUBLIC_URL:
        return f"{settings.S3_PUBLIC_URL.rstrip('/')}/{object_key}"
    return f"{settings.S3_ENDPOINT_URL}/{settings.S3_BUCKET_NAME}/{object_key}"


def _upload_to_local(content: bytes, user_id: int, filename: str) -> str:
    upload_dir = Path(__file__).resolve().parent.parent.parent / "uploads"
    user_dir = upload_dir / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)

    filepath = user_dir / filename
    with open(filepath, "wb") as f:
        f.write(content)

    return f"/uploads/{user_id}/{filename}"


async def delete_file(url: str) -> bool:
    """删除文件（尽力而为，不抛异常）"""
    try:
        if settings.use_s3 and not url.startswith("/uploads/"):
            client = _get_s3_client()
            if client:
                if settings.S3_PUBLIC_URL and url.startswith(settings.S3_PUBLIC_URL):
                    object_key = url[len(settings.S3_PUBLIC_URL.rstrip("/")) + 1:]
                else:
                    object_key = url.split(f"{settings.S3_BUCKET_NAME}/", 1)[-1]
                client.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=object_key)
                return True
        elif url.startswith("/uploads/"):
            upload_dir = Path(__file__).resolve().parent.parent.parent / "uploads"
            filepath = upload_dir / url.lstrip("/uploads/")
            if filepath.exists():
                filepath.unlink()
                return True
    except Exception as e:
        logger.warning(f"删除文件失败: {e}")
    return False
